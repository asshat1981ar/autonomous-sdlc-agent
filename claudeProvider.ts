import { AIProvider, AIGenerationConfig, AIResponse, AIProviderError } from './aiProviderInterface';

export class ClaudeProvider implements AIProvider {
    public readonly name = 'claude';
    private apiKey: string | null = null;
    private baseUrl = 'https://api.anthropic.com/v1';

    constructor() {
        this.apiKey = (window as any).CLAUDE_API_KEY || process.env.CLAUDE_API_KEY || process.env.ANTHROPIC_API_KEY;
    }

    isConfigured(): boolean {
        return this.apiKey !== null;
    }

    async generateContent(config: AIGenerationConfig): Promise<AIResponse> {
        if (!this.apiKey) {
            throw new AIProviderError('Claude API key not configured', { provider: this.name });
        }

        try {
            const model = config.model || 'claude-3-5-sonnet-20241022';
            
            // Prepare messages for Claude API
            const messages: any[] = [];
            
            // Add user message with text and optional images
            const userContent: any[] = [{ type: 'text', text: config.prompt }];
            
            // Add images if provided
            if (config.images && config.images.length > 0) {
                config.images.forEach(imageBase64 => {
                    userContent.push({
                        type: 'image',
                        source: {
                            type: 'base64',
                            media_type: 'image/png',
                            data: imageBase64
                        }
                    });
                });
            }

            messages.push({
                role: 'user',
                content: userContent
            });

            const requestBody: any = {
                model,
                messages,
                max_tokens: config.maxTokens || 2048,
                temperature: config.temperature || 0.7,
                stream: false
            };

            // Add system instruction if provided
            if (config.systemInstruction) {
                requestBody.system = config.systemInstruction;
            }

            // Add tools if provided (for function calling)
            if (config.tools && config.tools.length > 0) {
                requestBody.tools = config.tools;
            }

            const response = await fetch(`${this.baseUrl}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`,
                    'anthropic-version': '2023-06-01',
                    'User-Agent': 'Autonomous-SDLC-Agent/1.0'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(`Claude API error: ${response.status} ${response.statusText} - ${errorData.error?.message || 'Unknown error'}`);
            }

            const data = await response.json();
            
            if (!data.content || data.content.length === 0) {
                throw new Error('No response generated from Claude API');
            }

            // Extract text from content blocks
            const text = data.content
                .filter((block: any) => block.type === 'text')
                .map((block: any) => block.text)
                .join('\n');

            return {
                text,
                model,
                finishReason: data.stop_reason || 'stop',
                usage: {
                    promptTokens: data.usage?.input_tokens || 0,
                    completionTokens: data.usage?.output_tokens || 0,
                    totalTokens: (data.usage?.input_tokens || 0) + (data.usage?.output_tokens || 0)
                }
            };
        } catch (error) {
            const aiError = new AIProviderError(
                `Claude API error: ${error instanceof Error ? error.message : 'Unknown error'}`,
                { provider: this.name, details: error }
            );
            aiError.name = 'AIProviderError';
            throw aiError;
        }
    }

    // Claude-specific methods for enhanced code assistance
    async analyzeCodeQuality(code: string, language: string): Promise<string> {
        const prompt = `Analyze the quality of this ${language} code and provide detailed feedback:

\`\`\`${language}
${code}
\`\`\`

Please evaluate:
1. Code structure and organization
2. Performance considerations
3. Security vulnerabilities
4. Best practices adherence
5. Maintainability
6. Specific improvement recommendations

Provide a comprehensive analysis with actionable suggestions.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: `You are a senior software architect and code reviewer with expertise in ${language}. Provide thorough, constructive code analysis.`,
            temperature: 0.4
        });

        return response.text;
    }

    async generateTests(code: string, language: string, testFramework?: string): Promise<string> {
        const framework = testFramework || this.getDefaultTestFramework(language);
        
        const prompt = `Generate comprehensive unit tests for this ${language} code using ${framework}:

\`\`\`${language}
${code}
\`\`\`

Please include:
1. Test cases for normal functionality
2. Edge cases and error conditions
3. Mock objects where appropriate
4. Clear test descriptions
5. Setup and teardown if needed

Generate complete, runnable test code.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: `You are a test automation expert. Generate thorough, well-structured unit tests that follow ${framework} best practices.`,
            temperature: 0.3
        });

        return response.text;
    }

    async refactorCode(code: string, language: string, refactoringGoals: string[]): Promise<string> {
        const goals = refactoringGoals.join(', ');
        
        const prompt = `Refactor this ${language} code to improve: ${goals}

Original code:
\`\`\`${language}
${code}
\`\`\`

Please provide:
1. The refactored code
2. Explanation of changes made
3. Benefits of the refactoring
4. Any trade-offs or considerations

Focus on clean, maintainable code that follows SOLID principles.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: `You are an expert in code refactoring and software design patterns. Provide clean, well-structured refactored code with clear explanations.`,
            temperature: 0.4
        });

        return response.text;
    }

    async generateDocumentation(code: string, language: string, docType: 'api' | 'inline' | 'readme' = 'inline'): Promise<string> {
        let prompt = '';
        
        switch (docType) {
            case 'api':
                prompt = `Generate API documentation for this ${language} code:

\`\`\`${language}
${code}
\`\`\`

Include:
1. Function/method signatures
2. Parameter descriptions
3. Return value descriptions
4. Usage examples
5. Error conditions`;
                break;
                
            case 'readme':
                prompt = `Generate a README.md file for this ${language} code:

\`\`\`${language}
${code}
\`\`\`

Include:
1. Project description
2. Installation instructions
3. Usage examples
4. API reference
5. Contributing guidelines`;
                break;
                
            default: // inline
                prompt = `Add comprehensive inline documentation to this ${language} code:

\`\`\`${language}
${code}
\`\`\`

Include:
1. Function/class descriptions
2. Parameter documentation
3. Return value documentation
4. Usage examples in comments
5. Important implementation notes`;
        }

        const response = await this.generateContent({
            prompt,
            systemInstruction: `You are a technical writer specializing in software documentation. Create clear, comprehensive documentation that helps developers understand and use the code effectively.`,
            temperature: 0.5
        });

        return response.text;
    }

    async suggestArchitecture(requirements: string, constraints?: string): Promise<string> {
        const prompt = `Suggest a software architecture for the following requirements:

Requirements:
${requirements}

${constraints ? `Constraints:\n${constraints}` : ''}

Please provide:
1. High-level architecture overview
2. Component breakdown
3. Technology stack recommendations
4. Data flow design
5. Scalability considerations
6. Security considerations
7. Deployment strategy

Focus on modern, scalable, and maintainable architecture patterns.`;

        const response = await this.generateContent({
            prompt,
            systemInstruction: 'You are a senior software architect with expertise in designing scalable, maintainable systems. Provide comprehensive architectural guidance.',
            temperature: 0.6
        });

        return response.text;
    }

    private getDefaultTestFramework(language: string): string {
        const frameworks: Record<string, string> = {
            'javascript': 'Jest',
            'typescript': 'Jest',
            'python': 'pytest',
            'java': 'JUnit 5',
            'csharp': 'NUnit',
            'go': 'testing package',
            'rust': 'built-in test framework',
            'php': 'PHPUnit',
            'ruby': 'RSpec',
            'swift': 'XCTest',
            'kotlin': 'JUnit 5'
        };
        
        return frameworks[language.toLowerCase()] || 'appropriate testing framework';
    }
}

