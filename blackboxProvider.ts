import { AIProvider, AIGenerationConfig, AIResponse, AIProviderError } from './aiProviderInterface';

export class BlackboxProvider implements AIProvider {
    public readonly name = 'blackbox';
    private apiKey: string | null = null;
    private baseUrl = 'https://api.blackbox.ai/v1';

    constructor() {
        this.apiKey = (window as any).BLACKBOX_API_KEY || process.env.BLACKBOX_API_KEY;
    }

    isConfigured(): boolean {
        return this.apiKey !== null;
    }

    async generateContent(config: AIGenerationConfig): Promise<AIResponse> {
        if (!this.apiKey) {
            throw new AIProviderError('Blackbox API key not configured', { provider: this.name });
        }

        try {
            const model = config.model || 'blackbox-code';
            
            // Prepare the request payload for Blackbox API
            const requestBody = {
                model,
                messages: [
                    {
                        role: 'system',
                        content: config.systemInstruction || 'You are a helpful AI assistant specialized in code generation and software development.'
                    },
                    {
                        role: 'user',
                        content: config.prompt
                    }
                ],
                temperature: config.temperature || 0.7,
                max_tokens: config.maxTokens || 2048,
                stream: false
            };

            // Add image support if images are provided
            if (config.images && config.images.length > 0) {
                // Blackbox may support image inputs - adjust based on actual API
                requestBody.messages[1].content = [
                    { type: 'text', text: config.prompt },
                    ...config.images.map(imageBase64 => ({
                        type: 'image_url',
                        image_url: {
                            url: `data:image/png;base64,${imageBase64}`
                        }
                    }))
                ];
            }

            const response = await fetch(`${this.baseUrl}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`,
                    'User-Agent': 'Autonomous-SDLC-Agent/1.0'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`Blackbox API error: ${response.status} ${response.statusText} - ${errorData.error?.message || 'Unknown error'}`);
            }

            const data = await response.json();
            
            if (!data.choices || data.choices.length === 0) {
                throw new Error('No response generated from Blackbox API');
            }

            const choice = data.choices[0];
            const text = choice.message?.content || choice.text || '';

            return {
                text,
                model,
                finishReason: choice.finish_reason || 'stop',
                usage: {
                    promptTokens: data.usage?.prompt_tokens || 0,
                    completionTokens: data.usage?.completion_tokens || 0,
                    totalTokens: data.usage?.total_tokens || 0
                }
            };
        } catch (error) {
            const aiError = new AIProviderError(
                `Blackbox API error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                { provider: this.name, details: error }
            );
            aiError.name = 'AIProviderError';
            throw aiError;
        }
    }

    // Blackbox-specific methods for code generation
    async generateCode(language: string, description: string, context?: string): Promise<string> {
        const prompt = `Generate ${language} code for the following requirement:

Description: ${description}
${context ? `Context: ${context}` : ''}

Please provide clean, well-commented code that follows best practices.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: `You are an expert ${language} developer. Generate high-quality, production-ready code.`,
            temperature: 0.3 // Lower temperature for more deterministic code generation
        });

        return response.text;
    }

    async explainCode(code: string, language?: string): Promise<string> {
        const prompt = `Explain the following ${language || ''} code:

\`\`\`${language || ''}
${code}
\`\`\`

Please provide a clear explanation of what this code does, how it works, and any notable patterns or techniques used.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: 'You are a code reviewer and educator. Provide clear, educational explanations of code.',
            temperature: 0.5
        });

        return response.text;
    }

    async optimizeCode(code: string, language: string, optimizationGoals: string[] = ['performance', 'readability']): Promise<string> {
        const prompt = `Optimize the following ${language} code for ${optimizationGoals.join(', ')}:

\`\`\`${language}
${code}
\`\`\`

Please provide the optimized version with explanations of the improvements made.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: `You are a senior ${language} developer focused on code optimization. Provide improved code with clear explanations.`,
            temperature: 0.4
        });

        return response.text;
    }

    async debugCode(code: string, error: string, language: string): Promise<string> {
        const prompt = `Debug the following ${language} code that is producing this error:

Error: ${error}

Code:
\`\`\`${language}
${code}
\`\`\`

Please identify the issue and provide a corrected version with explanation.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: `You are an expert debugger. Identify issues in code and provide clear fixes with explanations.`,
            temperature: 0.3
        });

        return response.text;
    }
}

