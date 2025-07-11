// AI Provider Interface for abstracting different AI services
export interface AIProvider {
    name: string;
    isConfigured(): boolean;
    generateContent(config: AIGenerationConfig): Promise<AIResponse>;
}

export interface AIGenerationConfig {
    prompt: string;
    model?: string;
    temperature?: number;
    maxTokens?: number;
    systemInstruction?: string;
    tools?: any[];
    responseMimeType?: string;
    images?: string[]; // Base64 encoded images
}

export interface AIResponse {
    text: string;
    usage?: {
        promptTokens: number;
        completionTokens: number;
        totalTokens: number;
    };
    model?: string;
    finishReason?: string;
}

export interface AIProviderError extends Error {
    provider: string;
    code?: string;
    details?: any;
}

// Factory for creating AI providers
export class AIProviderFactory {
    private static providers: Map<string, AIProvider> = new Map();
    private static initialized = false;

    static initialize(): void {
        if (this.initialized) return;
        
        // Import and register all providers
        import('./geminiProvider').then(({ GeminiProvider }) => {
            this.registerProvider('gemini', new GeminiProvider());
        }).catch(console.error);
        
        import('./blackboxProvider').then(({ BlackboxProvider }) => {
            this.registerProvider('blackbox', new BlackboxProvider());
        }).catch(console.error);
        
        import('./claudeProvider').then(({ ClaudeProvider }) => {
            this.registerProvider('claude', new ClaudeProvider());
        }).catch(console.error);
        
        this.initialized = true;
    }

    static registerProvider(name: string, provider: AIProvider): void {
        this.providers.set(name, provider);
    }

    static getProvider(name: string): AIProvider | null {
        if (!this.initialized) {
            this.initialize();
        }
        return this.providers.get(name) || null;
    }

    static getAvailableProviders(): string[] {
        if (!this.initialized) {
            this.initialize();
        }
        return Array.from(this.providers.keys()).filter(name => 
            this.providers.get(name)?.isConfigured()
        );
    }

    static getAllProviders(): string[] {
        if (!this.initialized) {
            this.initialize();
        }
        return Array.from(this.providers.keys());
    }

    static getDefaultProvider(): AIProvider | null {
        const available = this.getAvailableProviders();
        if (available.length === 0) return null;
        
        // Priority order: Claude, Gemini, Blackbox, others
        const priority = ['claude', 'gemini', 'blackbox'];
        for (const providerName of priority) {
            if (available.includes(providerName)) {
                return this.getProvider(providerName);
            }
        }
        
        return this.getProvider(available[0]);
    }

    static async switchProvider(providerName: string): Promise<AIProvider | null> {
        const provider = this.getProvider(providerName);
        if (!provider) {
            throw new Error(`Provider '${providerName}' not found`);
        }
        if (!provider.isConfigured()) {
            throw new Error(`Provider '${providerName}' is not configured`);
        }
        return provider;
    }

    static getProviderCapabilities(providerName: string): string[] {
        const capabilities: Record<string, string[]> = {
            'gemini': ['text-generation', 'image-understanding', 'multimodal', 'function-calling'],
            'claude': ['text-generation', 'image-understanding', 'code-analysis', 'reasoning', 'function-calling'],
            'blackbox': ['code-generation', 'code-explanation', 'code-optimization', 'debugging']
        };
        
        return capabilities[providerName] || ['text-generation'];
    }
}

