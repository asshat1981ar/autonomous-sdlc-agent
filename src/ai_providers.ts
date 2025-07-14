import fetch from 'node-fetch';

export interface AIProvider {
  generate_response(prompt: string): Promise<{ response: string }>;
}

interface OpenRouterRequestMessage {
  role: string;
  content: Array<{ type: string; text?: string; image_url?: { url: string }; file?: { filename: string; file_data: string } }>;
}

interface OpenRouterResponseChoice {
  message: {
    role: string;
    content: Array<{ type: string; text?: string }>;
  };
}

interface OpenRouterResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: OpenRouterResponseChoice[];
}

interface AIProviderOptions {
  apiKey: string;
  systemPrompt: string;
  model?: string;
}

export class OpenRouterAIProvider implements AIProvider {
  private apiKey: string;
  private systemPrompt: string;
  private model: string;

  constructor(options: AIProviderOptions) {
    this.apiKey = options.apiKey;
    this.systemPrompt = options.systemPrompt;
    this.model = options.model || 'openai/gpt-4o';
  }

  private buildMessages(userPrompt: string) : OpenRouterRequestMessage[] {
    return [
      {
        role: 'system',
        content: [
          { type: 'text', text: this.systemPrompt }
        ]
      },
      {
        role: 'user',
        content: [
          { type: 'text', text: userPrompt }
        ]
      }
    ];
  }

  async generate_response(userPrompt: string): Promise<{ response: string }> {
    const url = 'https://openrouter.ai/api/v1/chat/completions';
    const messages = this.buildMessages(userPrompt);

    const body = {
      model: this.model,
      messages: messages,
    };

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
    };

    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`OpenRouter API error: ${res.status} ${res.statusText} - ${errorText}`);
      }

      const data: OpenRouterResponse = await res.json();

      if (data.choices && data.choices.length > 0) {
        const textBlocks = data.choices[0].message.content;
        const combinedText = textBlocks.map(block => block.text || '').join('');
        return { response: combinedText.trim() };
      } else {
        throw new Error('No response choices from OpenRouter API');
      }
    } catch (error) {
      throw new Error(`Failed to generate response: ${error.message}`);
    }
  }
}
