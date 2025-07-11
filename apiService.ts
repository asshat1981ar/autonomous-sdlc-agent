// API service for exposing RESTful endpoints
import { AppIdea, AppPlan, ProjectFile, IdeationResult } from '../types';
import { emitWebhookEvent } from './webhookService';

export interface APIResponse<T = any> {
    success: boolean;
    data?: T;
    error?: string;
    timestamp: string;
}

export interface ProjectCreateRequest {
    idea: AppIdea;
    options?: {
        skipIdeation?: boolean;
        customPersonas?: string[];
    };
}

export interface CodeGenerationRequest {
    projectId: string;
    filePath: string;
    context?: {
        relatedFiles?: string[];
        requirements?: string;
    };
}

export interface WebhookSubscriptionRequest {
    url: string;
    events: string[];
    secret?: string;
    headers?: Record<string, string>;
}

class APIService {
    private baseUrl: string;
    private projects: Map<string, { plan: AppPlan; files: ProjectFile[] }> = new Map();

    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
    }

    // Project Management Endpoints
    async createProject(request: ProjectCreateRequest): Promise<APIResponse<{ projectId: string; plan?: AppPlan }>> {
        try {
            const projectId = crypto.randomUUID();
            
            // Emit webhook event
            await emitWebhookEvent('project.created', {
                projectId,
                idea: request.idea,
                options: request.options
            });

            // In a real implementation, this would integrate with the existing orchestrator
            // For now, return a mock response
            return {
                success: true,
                data: { projectId },
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    async getProject(projectId: string): Promise<APIResponse<{ plan: AppPlan; files: ProjectFile[] }>> {
        try {
            const project = this.projects.get(projectId);
            if (!project) {
                return {
                    success: false,
                    error: 'Project not found',
                    timestamp: new Date().toISOString()
                };
            }

            return {
                success: true,
                data: project,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    async updateProject(projectId: string, updates: Partial<AppPlan>): Promise<APIResponse<AppPlan>> {
        try {
            const project = this.projects.get(projectId);
            if (!project) {
                return {
                    success: false,
                    error: 'Project not found',
                    timestamp: new Date().toISOString()
                };
            }

            const updatedPlan = { ...project.plan, ...updates };
            this.projects.set(projectId, { ...project, plan: updatedPlan });

            await emitWebhookEvent('project.updated', {
                projectId,
                updates,
                plan: updatedPlan
            });

            return {
                success: true,
                data: updatedPlan,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    async deleteProject(projectId: string): Promise<APIResponse<void>> {
        try {
            const deleted = this.projects.delete(projectId);
            if (!deleted) {
                return {
                    success: false,
                    error: 'Project not found',
                    timestamp: new Date().toISOString()
                };
            }

            return {
                success: true,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    // Code Generation Endpoints
    async generateCode(request: CodeGenerationRequest): Promise<APIResponse<{ code: string; filePath: string }>> {
        try {
            await emitWebhookEvent('code.generated', {
                projectId: request.projectId,
                filePath: request.filePath,
                context: request.context
            });

            // In a real implementation, this would integrate with the code generation service
            return {
                success: true,
                data: {
                    code: '// Generated code placeholder',
                    filePath: request.filePath
                },
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    async updateCode(projectId: string, filePath: string, code: string): Promise<APIResponse<ProjectFile>> {
        try {
            const project = this.projects.get(projectId);
            if (!project) {
                return {
                    success: false,
                    error: 'Project not found',
                    timestamp: new Date().toISOString()
                };
            }

            // Find and update the file
            const updateFile = (files: ProjectFile[]): boolean => {
                for (const file of files) {
                    if (file.path === filePath) {
                        file.code = code;
                        file.status = 'modified';
                        return true;
                    }
                    if (file.children && updateFile(file.children)) {
                        return true;
                    }
                }
                return false;
            };

            const updated = updateFile(project.files);
            if (!updated) {
                return {
                    success: false,
                    error: 'File not found',
                    timestamp: new Date().toISOString()
                };
            }

            await emitWebhookEvent('code.updated', {
                projectId,
                filePath,
                code
            });

            const updatedFile = project.files.find(f => f.path === filePath);
            return {
                success: true,
                data: updatedFile!,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    // Webhook Management Endpoints
    async subscribeWebhook(request: WebhookSubscriptionRequest): Promise<APIResponse<{ subscriptionId: string }>> {
        try {
            // This would integrate with the webhook service
            const subscriptionId = crypto.randomUUID();
            
            return {
                success: true,
                data: { subscriptionId },
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    async unsubscribeWebhook(subscriptionId: string): Promise<APIResponse<void>> {
        try {
            // This would integrate with the webhook service
            return {
                success: true,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Unknown error',
                timestamp: new Date().toISOString()
            };
        }
    }

    // Health and Status Endpoints
    async getHealth(): Promise<APIResponse<{ status: string; version: string; uptime: number }>> {
        return {
            success: true,
            data: {
                status: 'healthy',
                version: '1.0.0',
                uptime: Date.now()
            },
            timestamp: new Date().toISOString()
        };
    }

    async getMetrics(): Promise<APIResponse<{ projects: number; activeWebhooks: number }>> {
        return {
            success: true,
            data: {
                projects: this.projects.size,
                activeWebhooks: 0 // Would come from webhook service
            },
            timestamp: new Date().toISOString()
        };
    }
}

// Export singleton instance
export const apiService = new APIService();

// OpenAPI Schema for documentation
export const openApiSchema = {
    openapi: '3.0.0',
    info: {
        title: 'Autonomous SDLC Agent API',
        version: '1.0.0',
        description: 'RESTful API for the Autonomous SDLC Agent'
    },
    servers: [
        {
            url: '/api/v1',
            description: 'API v1'
        }
    ],
    paths: {
        '/projects': {
            post: {
                summary: 'Create a new project',
                requestBody: {
                    required: true,
                    content: {
                        'application/json': {
                            schema: {
                                type: 'object',
                                properties: {
                                    idea: {
                                        type: 'object',
                                        properties: {
                                            prompt: { type: 'string' },
                                            githubRepoUrl: { type: 'string' }
                                        },
                                        required: ['prompt']
                                    },
                                    options: {
                                        type: 'object',
                                        properties: {
                                            skipIdeation: { type: 'boolean' },
                                            customPersonas: {
                                                type: 'array',
                                                items: { type: 'string' }
                                            }
                                        }
                                    }
                                },
                                required: ['idea']
                            }
                        }
                    }
                },
                responses: {
                    '200': {
                        description: 'Project created successfully',
                        content: {
                            'application/json': {
                                schema: {
                                    type: 'object',
                                    properties: {
                                        success: { type: 'boolean' },
                                        data: {
                                            type: 'object',
                                            properties: {
                                                projectId: { type: 'string' }
                                            }
                                        },
                                        timestamp: { type: 'string' }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        '/projects/{projectId}': {
            get: {
                summary: 'Get project details',
                parameters: [
                    {
                        name: 'projectId',
                        in: 'path',
                        required: true,
                        schema: { type: 'string' }
                    }
                ],
                responses: {
                    '200': {
                        description: 'Project details retrieved successfully'
                    },
                    '404': {
                        description: 'Project not found'
                    }
                }
            }
        },
        '/webhooks': {
            post: {
                summary: 'Subscribe to webhook events',
                requestBody: {
                    required: true,
                    content: {
                        'application/json': {
                            schema: {
                                type: 'object',
                                properties: {
                                    url: { type: 'string' },
                                    events: {
                                        type: 'array',
                                        items: { type: 'string' }
                                    },
                                    secret: { type: 'string' }
                                },
                                required: ['url', 'events']
                            }
                        }
                    }
                },
                responses: {
                    '200': {
                        description: 'Webhook subscription created successfully'
                    }
                }
            }
        },
        '/health': {
            get: {
                summary: 'Get service health status',
                responses: {
                    '200': {
                        description: 'Service health status'
                    }
                }
            }
        }
    }
};

