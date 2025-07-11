import { GoogleGenAI } from "@google/genai";
import { AIProvider, AIGenerationConfig, AIResponse, AIProviderError } from './aiProviderInterface';

export class GeminiProvider implements AIProvider {
    public readonly name = 'gemini';
    private ai: GoogleGenAI | null = null;

    constructor() {
        const apiKey = (window as any).GEMINI_API_KEY || process.env.GEMINI_API_KEY;
        if (apiKey) {
            this.ai = new GoogleGenAI({ apiKey });
        }
    }

    isConfigured(): boolean {
        return this.ai !== null;
    }

    async generateContent(config: AIGenerationConfig): Promise<AIResponse> {
        if (!this.ai) {
            throw new AIProviderError('Gemini API key not configured', { provider: this.name });
        }

        try {
            const model = config.model || 'gemini-2.5-flash-preview-04-17';
            
            // Prepare content parts
            const parts: any[] = [{ text: config.prompt }];
            
            // Add images if provided
            if (config.images && config.images.length > 0) {
                config.images.forEach(imageBase64 => {
                    parts.push({
                        inlineData: {
                            mimeType: 'image/png',
                            data: imageBase64,
                        },
                    });
                });
            }

            const requestConfig: any = {
                contents: { parts },
                config: {
                    temperature: config.temperature || 0.7,
                    maxOutputTokens: config.maxTokens,
                    systemInstruction: config.systemInstruction,
                    tools: config.tools,
                    responseMimeType: config.responseMimeType,
                }
            };

            const response = await this.ai.models.generateContent({ 
                model, 
                ...requestConfig 
            });

            return {
                text: response.text,
                model,
                finishReason: 'stop', // Gemini doesn't provide finish reason in the same format
                usage: {
                    promptTokens: 0, // Gemini doesn't provide token usage in the same format
                    completionTokens: 0,
                    totalTokens: 0
                }
            };
        } catch (error) {
            const aiError = new AIProviderError(
                `Gemini API error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                { provider: this.name, details: error }
            );
            aiError.name = 'AIProviderError';
            throw aiError;
        }
    }
}

