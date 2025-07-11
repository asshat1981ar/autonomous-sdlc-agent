// services/feedbackLoopService.ts
import { AgentName, ProjectFile, AppPlan } from "../types";

export interface FeedbackMetrics {
  sessionId: string;
  projectId: string;
  timestamp: string;
  userActions: UserAction[];
  codeGenerationMetrics: CodeGenerationMetric[];
  agentPerformance: AgentPerformanceMetric[];
  systemReliability: SystemReliabilityMetric[];
}

export interface UserAction {
  action: 'generate_code' | 'modify_code' | 'test_code' | 'chat_message' | 'satisfaction_feedback' | 'iteration_request';
  timestamp: string;
  context: string;
  satisfactionScore?: number;
  iterationCount: number;
  timeSpent?: number;
}

export interface CodeGenerationMetric {
  filePath: string;
  agent: AgentName;
  success: boolean;
  generationTime: number;
  compilationSuccess: boolean;
  userApproval: boolean;
  errorType?: string;
  promptTokens?: number;
  responseTokens?: number;
}

export interface AgentPerformanceMetric {
  agent: AgentName;
  taskType: string;
  completionTime: number;
  successRate: number;
  userSatisfaction: number;
  handoffEfficiency?: number;
}

export interface SystemReliabilityMetric {
  apiProvider: string;
  responseTime: number;
  successRate: number;
  fallbackActivated: boolean;
  errorType?: string;
}

export interface SuccessPattern {
  id: string;
  context: string;
  prompt: string;
  outcome: string;
  successScore: number;
  conditions: Record<string, any>;
}

export interface OptimizedPrompt {
  basePrompt: string;
  contextModifications: string[];
  successModifiers: string[];
  adaptiveParameters: Record<string, any>;
}

export interface PredictiveInsight {
  type: 'suggestion' | 'warning' | 'optimization' | 'assistance';
  confidence: number;
  message: string;
  actionable: boolean;
  context: string;
}

export class FeedbackCollectionService {
  private static instance: FeedbackCollectionService;
  private metrics: FeedbackMetrics[] = [];
  private currentSession: string;
  
  private constructor() {
    this.currentSession = this.generateSessionId();
  }
  
  static getInstance(): FeedbackCollectionService {
    if (!this.instance) {
      this.instance = new FeedbackCollectionService();
    }
    return this.instance;
  }
  
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  collectUserAction(action: UserAction): void {
    const currentMetrics = this.getCurrentSessionMetrics();
    currentMetrics.userActions.push({
      ...action,
      timestamp: action.timestamp || new Date().toISOString()
    });
    this.persistMetrics();
  }
  
  collectCodeGeneration(metric: CodeGenerationMetric): void {
    const currentMetrics = this.getCurrentSessionMetrics();
    currentMetrics.codeGenerationMetrics.push(metric);
    this.persistMetrics();
  }
  
  collectAgentPerformance(metric: AgentPerformanceMetric): void {
    const currentMetrics = this.getCurrentSessionMetrics();
    currentMetrics.agentPerformance.push(metric);
    this.persistMetrics();
  }
  
  collectSystemReliability(metric: SystemReliabilityMetric): void {
    const currentMetrics = this.getCurrentSessionMetrics();
    currentMetrics.systemReliability.push(metric);
    this.persistMetrics();
  }
  
  private getCurrentSessionMetrics(): FeedbackMetrics {
    let current = this.metrics.find(m => m.sessionId === this.currentSession);
    if (!current) {
      current = {
        sessionId: this.currentSession,
        projectId: `project_${Date.now()}`,
        timestamp: new Date().toISOString(),
        userActions: [],
        codeGenerationMetrics: [],
        agentPerformance: [],
        systemReliability: []
      };
      this.metrics.push(current);
    }
    return current;
  }
  
  private persistMetrics(): void {
    // Store in localStorage for persistence across sessions
    localStorage.setItem('sdlc_feedback_metrics', JSON.stringify(this.metrics));
  }
  
  loadPersistedMetrics(): void {
    const stored = localStorage.getItem('sdlc_feedback_metrics');
    if (stored) {
      this.metrics = JSON.parse(stored);
    }
  }
  
  getMetrics(): FeedbackMetrics[] {
    return this.metrics;
  }
  
  getSessionMetrics(sessionId?: string): FeedbackMetrics | undefined {
    return this.metrics.find(m => m.sessionId === (sessionId || this.currentSession));
  }

  getCurrentSession(): string {
    return this.currentSession;
  }
}

export class AnalyticsEngine {
  private feedbackService: FeedbackCollectionService;
  private learningMemory: LearningMemory;
  
  constructor() {
    this.feedbackService = FeedbackCollectionService.getInstance();
    this.learningMemory = new LearningMemory();
  }
  
  analyzeCodeGenerationPatterns(): PromptOptimization[] {
    const metrics = this.feedbackService.getMetrics();
    const codeGenMetrics = metrics.flatMap(m => m.codeGenerationMetrics);
    
    const optimizations: PromptOptimization[] = [];
    
    // Analyze success patterns by agent
    const agentSuccessRates = this.calculateAgentSuccessRates(codeGenMetrics);
    
    // Analyze success patterns by file type
    const fileTypePatterns = this.analyzeFileTypePatterns(codeGenMetrics);
    
    // Analyze timing patterns
    const timingPatterns = this.analyzeTimingPatterns(codeGenMetrics);
    
    // Generate optimizations based on patterns
    Object.entries(agentSuccessRates).forEach(([agent, rate]) => {
      if (rate < 0.85) {
        optimizations.push({
          agent: agent as AgentName,
          type: 'prompt_enhancement',
          suggestion: `Improve prompts for ${agent} - current success rate: ${(rate * 100).toFixed(1)}%`,
          priority: 'high'
        });
      }
    });
    
    return optimizations;
  }
  
  analyzeAgentPerformance(): AgentOptimization[] {
    const metrics = this.feedbackService.getMetrics();
    const agentMetrics = metrics.flatMap(m => m.agentPerformance);
    
    const optimizations: AgentOptimization[] = [];
    
    // Group by agent and analyze performance
    const agentGroups = this.groupBy(agentMetrics, 'agent');
    
    Object.entries(agentGroups).forEach(([agent, metrics]) => {
      const avgCompletionTime = metrics.reduce((sum, m) => sum + m.completionTime, 0) / metrics.length;
      const avgSuccessRate = metrics.reduce((sum, m) => sum + m.successRate, 0) / metrics.length;
      const avgSatisfaction = metrics.reduce((sum, m) => sum + m.userSatisfaction, 0) / metrics.length;
      
      if (avgSuccessRate < 0.9) {
        optimizations.push({
          agent: agent as AgentName,
          type: 'capability_enhancement',
          currentPerformance: avgSuccessRate,
          targetPerformance: 0.95,
          suggestion: `Enhance ${agent} capabilities - current success rate: ${(avgSuccessRate * 100).toFixed(1)}%`
        });
      }
      
      if (avgCompletionTime > 30000) { // 30 seconds
        optimizations.push({
          agent: agent as AgentName,
          type: 'performance_optimization',
          currentPerformance: avgCompletionTime,
          targetPerformance: 20000,
          suggestion: `Optimize ${agent} performance - current avg time: ${(avgCompletionTime / 1000).toFixed(1)}s`
        });
      }
    });
    
    return optimizations;
  }
  
  predictUserNeeds(sessionContext: SessionContext): PredictiveInsight[] {
    const insights: PredictiveInsight[] = [];
    const sessionMetrics = this.feedbackService.getSessionMetrics();
    
    if (!sessionMetrics) return insights;
    
    // Analyze user action patterns
    const actions = sessionMetrics.userActions;
    const recentActions = actions.slice(-5); // Last 5 actions
    
    // Predict likely next actions
    if (this.hasPattern(recentActions, ['generate_code', 'modify_code'])) {
      insights.push({
        type: 'suggestion',
        confidence: 0.8,
        message: 'You might want to test the generated code next',
        actionable: true,
        context: 'code_generation_workflow'
      });
    }
    
    // Detect frustration patterns
    const highIterationActions = actions.filter(a => a.iterationCount > 3);
    if (highIterationActions.length > 2) {
      insights.push({
        type: 'assistance',
        confidence: 0.9,
        message: 'I notice you\'re iterating frequently. Would you like me to suggest alternative approaches?',
        actionable: true,
        context: 'user_frustration'
      });
    }
    
    // Predict quality issues
    const codeGenMetrics = sessionMetrics.codeGenerationMetrics;
    const recentFailures = codeGenMetrics.filter(m => !m.success || !m.compilationSuccess).slice(-3);
    if (recentFailures.length >= 2) {
      insights.push({
        type: 'warning',
        confidence: 0.75,
        message: 'Potential quality issues detected. Consider reviewing the project requirements.',
        actionable: true,
        context: 'quality_assurance'
      });
    }
    
    return insights;
  }
  
  identifyBottlenecks(): SystemOptimization[] {
    const metrics = this.feedbackService.getMetrics();
    const optimizations: SystemOptimization[] = [];
    
    // Analyze API performance
    const reliabilityMetrics = metrics.flatMap(m => m.systemReliability);
    const apiGroups = this.groupBy(reliabilityMetrics, 'apiProvider');
    
    Object.entries(apiGroups).forEach(([provider, metrics]) => {
      const avgResponseTime = metrics.reduce((sum, m) => sum + m.responseTime, 0) / metrics.length;
      const successRate = metrics.filter(m => m.successRate > 0.95).length / metrics.length;
      
      if (avgResponseTime > 5000) { // 5 seconds
        optimizations.push({
          type: 'api_performance',
          provider,
          issue: 'slow_response_time',
          currentValue: avgResponseTime,
          targetValue: 3000,
          suggestion: `Optimize ${provider} API calls - current avg response: ${(avgResponseTime / 1000).toFixed(1)}s`
        });
      }
      
      if (successRate < 0.95) {
        optimizations.push({
          type: 'api_reliability',
          provider,
          issue: 'low_success_rate',
          currentValue: successRate,
          targetValue: 0.98,
          suggestion: `Improve ${provider} reliability - current success rate: ${(successRate * 100).toFixed(1)}%`
        });
      }
    });
    
    return optimizations;
  }
  
  private calculateAgentSuccessRates(metrics: CodeGenerationMetric[]): Record<string, number> {
    const agentGroups = this.groupBy(metrics, 'agent');
    const successRates: Record<string, number> = {};
    
    Object.entries(agentGroups).forEach(([agent, metrics]) => {
      const successCount = metrics.filter(m => m.success && m.compilationSuccess && m.userApproval).length;
      successRates[agent] = successCount / metrics.length;
    });
    
    return successRates;
  }
  
  private analyzeFileTypePatterns(metrics: CodeGenerationMetric[]): Record<string, number> {
    const fileTypeGroups = this.groupBy(metrics, m => this.getFileExtension(m.filePath));
    const patterns: Record<string, number> = {};
    
    Object.entries(fileTypeGroups).forEach(([fileType, metrics]) => {
      const successCount = metrics.filter(m => m.success).length;
      patterns[fileType] = successCount / metrics.length;
    });
    
    return patterns;
  }
  
  private analyzeTimingPatterns(metrics: CodeGenerationMetric[]): Record<string, number> {
    const avgTimes: Record<string, number> = {};
    const agentGroups = this.groupBy(metrics, 'agent');
    
    Object.entries(agentGroups).forEach(([agent, metrics]) => {
      const avgTime = metrics.reduce((sum, m) => sum + m.generationTime, 0) / metrics.length;
      avgTimes[agent] = avgTime;
    });
    
    return avgTimes;
  }
  
  private getFileExtension(filePath: string): string {
    return filePath.split('.').pop() || 'unknown';
  }
  
  private groupBy<T>(array: T[], key: keyof T | ((item: T) => string)): Record<string, T[]> {
    return array.reduce((groups, item) => {
      const groupKey = typeof key === 'function' ? key(item) : String(item[key]);
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(item);
      return groups;
    }, {} as Record<string, T[]>);
  }
  
  private hasPattern(actions: UserAction[], pattern: string[]): boolean {
    if (actions.length < pattern.length) return false;
    
    const recentActionTypes = actions.slice(-pattern.length).map(a => a.action);
    return pattern.every((expectedAction, index) => recentActionTypes[index] === expectedAction);
  }
}

export class AdaptiveOptimizer {
  private analyticsEngine: AnalyticsEngine;
  private learningMemory: LearningMemory;
  
  constructor() {
    this.analyticsEngine = new AnalyticsEngine();
    this.learningMemory = new LearningMemory();
  }
  
  optimizePrompts(context: GenerationContext): OptimizedPrompt {
    const relevantKnowledge = this.learningMemory.retrieveRelevantKnowledge(context);
    const successPatterns = relevantKnowledge.filter(k => k.type === 'success_pattern');
    
    const basePrompt = context.originalPrompt;
    const contextModifications: string[] = [];
    const successModifiers: string[] = [];
    
    // Apply learned optimizations
    successPatterns.forEach(pattern => {
      if (pattern.confidence > 0.8) {
        successModifiers.push(pattern.modification);
      }
    });
    
    // Add context-specific improvements
    if (context.fileType === 'tsx' && context.hasComponents) {
      contextModifications.push("Ensure proper TypeScript typing and React best practices.");
    }
    
    if (context.previousFailures > 2) {
      contextModifications.push("Focus on simplicity and correctness over complexity.");
    }
    
    return {
      basePrompt,
      contextModifications,
      successModifiers,
      adaptiveParameters: {
        temperature: Math.max(0.1, 0.7 - (context.previousFailures * 0.1)),
        maxTokens: context.complexity === 'high' ? 4000 : 2000
      }
    };
  }
  
  optimizeAgentAssignment(task: Task): AgentName {
    const agentPerformance = this.analyticsEngine.analyzeAgentPerformance();
    
    // Find best performing agent for this task type
    const relevantAgents = agentPerformance.filter(ap => 
      this.isAgentSuitableForTask(ap.agent, task.type)
    );
    
    if (relevantAgents.length === 0) {
      return this.getDefaultAgentForTask(task.type);
    }
    
    // Sort by performance score (combination of success rate and user satisfaction)
    relevantAgents.sort((a, b) => {
      const scoreA = a.currentPerformance * 0.7 + (a as any).userSatisfaction * 0.3;
      const scoreB = b.currentPerformance * 0.7 + (b as any).userSatisfaction * 0.3;
      return scoreB - scoreA;
    });
    
    return relevantAgents[0].agent;
  }
  
  optimizeAIProviderSelection(context: TaskContext): 'gemini' | 'deepseek' | 'claude-code' {
    const systemOptimizations = this.analyticsEngine.identifyBottlenecks();
    const providerPerformance = new Map();
    
    // Calculate provider scores based on reliability and performance
    systemOptimizations.forEach(opt => {
      if (opt.type === 'api_performance' || opt.type === 'api_reliability') {
        const score = 1 - (opt.currentValue / opt.targetValue);
        providerPerformance.set(opt.provider, score);
      }
    });
    
    // Select best provider for task type
    if (context.taskType === 'code_generation' && providerPerformance.get('claude-code') > 0.8) {
      return 'claude-code';
    } else if (context.taskType === 'ideation' && providerPerformance.get('gemini') > 0.8) {
      return 'gemini';
    } else if (context.complexity === 'high' && providerPerformance.get('deepseek') > 0.8) {
      return 'deepseek';
    }
    
    // Default fallback logic
    return 'gemini';
  }
  
  generatePredictiveRecommendations(): Recommendation[] {
    const insights = this.analyticsEngine.predictUserNeeds({} as SessionContext);
    
    return insights.map(insight => ({
      type: insight.type,
      priority: insight.confidence > 0.8 ? 'high' : 'medium',
      message: insight.message,
      actionable: insight.actionable,
      context: insight.context,
      confidence: insight.confidence
    }));
  }
  
  private isAgentSuitableForTask(agent: AgentName, taskType: string): boolean {
    const agentTaskMapping: Record<AgentName, string[]> = {
      'Frontend Expert': ['component_generation', 'styling', 'ui_development'],
      'Backend Expert': ['api_development', 'server_logic', 'database_integration'],
      'Full-Stack Developer': ['general_development', 'integration', 'configuration'],
      'QA Engineer': ['testing', 'quality_assurance', 'debugging'],
      'DevOps Engineer': ['deployment', 'ci_cd', 'infrastructure'],
      'Security Analyst': ['security_audit', 'vulnerability_assessment'],
      // ... other agent mappings
    } as any;
    
    return agentTaskMapping[agent]?.includes(taskType) || false;
  }
  
  private getDefaultAgentForTask(taskType: string): AgentName {
    const defaultMapping: Record<string, AgentName> = {
      'component_generation': 'Frontend Expert',
      'api_development': 'Backend Expert',
      'general_development': 'Full-Stack Developer',
      'testing': 'QA Engineer',
      'deployment': 'DevOps Engineer'
    };
    
    return defaultMapping[taskType] || 'Full-Stack Developer';
  }
}

export class LearningMemory {
  private knowledgeBase: Map<string, KnowledgeEntry> = new Map();
  
  storeSuccessPattern(pattern: SuccessPattern): void {
    const key = this.generateKnowledgeKey(pattern.context);
    const existing = this.knowledgeBase.get(key);
    
    if (existing) {
      existing.successPatterns = existing.successPatterns || [];
      existing.successPatterns.push(pattern);
      existing.confidence = this.calculateConfidence(existing.successPatterns);
    } else {
      this.knowledgeBase.set(key, {
        id: key,
        type: 'success_pattern',
        context: pattern.context,
        successPatterns: [pattern],
        confidence: pattern.successScore,
        lastUpdated: new Date().toISOString(),
        modification: pattern.prompt
      });
    }
    
    this.persistKnowledge();
  }
  
  storeFailurePattern(pattern: FailurePattern): void {
    const key = this.generateKnowledgeKey(pattern.context);
    const existing = this.knowledgeBase.get(key);
    
    if (existing) {
      existing.failurePatterns = existing.failurePatterns || [];
      existing.failurePatterns.push(pattern);
    } else {
      this.knowledgeBase.set(key, {
        id: key,
        type: 'failure_pattern',
        context: pattern.context,
        failurePatterns: [pattern],
        confidence: 1 - pattern.failureScore,
        lastUpdated: new Date().toISOString(),
        modification: `Avoid: ${pattern.approach}`
      });
    }
    
    this.persistKnowledge();
  }
  
  retrieveRelevantKnowledge(context: Context): KnowledgeEntry[] {
    const relevant: KnowledgeEntry[] = [];
    
    this.knowledgeBase.forEach(entry => {
      const relevanceScore = this.calculateRelevance(entry.context, context);
      if (relevanceScore > 0.5) {
        relevant.push({
          ...entry,
          relevanceScore
        });
      }
    });
    
    // Sort by relevance and confidence
    return relevant.sort((a, b) => {
      const scoreA = (a.relevanceScore || 0) * 0.6 + a.confidence * 0.4;
      const scoreB = (b.relevanceScore || 0) * 0.6 + (b.confidence || 0) * 0.4;
      return scoreB - scoreA;
    });
  }
  
  evolveKnowledge(): void {
    const cutoffDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000); // 30 days ago
    
    this.knowledgeBase.forEach((entry, key) => {
      const lastUpdated = new Date(entry.lastUpdated);
      
      // Remove outdated entries with low confidence
      if (lastUpdated < cutoffDate && entry.confidence < 0.3) {
        this.knowledgeBase.delete(key);
      }
      
      // Decay confidence over time
      if (lastUpdated < cutoffDate) {
        entry.confidence = (entry.confidence || 0) * 0.9;
      }
    });
    
    this.persistKnowledge();
  }
  
  private generateKnowledgeKey(context: string): string {
    return `knowledge_${context.replace(/\s+/g, '_').toLowerCase()}`;
  }
  
  private calculateConfidence(patterns: SuccessPattern[]): number {
    const avgSuccess = patterns.reduce((sum, p) => sum + p.successScore, 0) / patterns.length;
    const sampleSize = Math.min(patterns.length / 10, 1); // More samples = higher confidence
    return avgSuccess * sampleSize;
  }
  
  private calculateRelevance(entryContext: string, queryContext: Context): number {
    // Simple keyword-based relevance for now
    const entryKeywords = entryContext.toLowerCase().split(/\s+/);
    const queryKeywords = JSON.stringify(queryContext).toLowerCase().split(/\s+/);
    
    const commonKeywords = entryKeywords.filter(k => queryKeywords.includes(k));
    return commonKeywords.length / Math.max(entryKeywords.length, queryKeywords.length);
  }
  
  private persistKnowledge(): void {
    const serialized = JSON.stringify(Array.from(this.knowledgeBase.entries()));
    localStorage.setItem('sdlc_learning_memory', serialized);
  }
  
  loadPersistedKnowledge(): void {
    const stored = localStorage.getItem('sdlc_learning_memory');
    if (stored) {
      const entries = JSON.parse(stored);
      this.knowledgeBase = new Map(entries);
    }
  }
}

// Type definitions for interfaces used above
interface PromptOptimization {
  agent: AgentName;
  type: 'prompt_enhancement' | 'context_optimization' | 'parameter_tuning';
  suggestion: string;
  priority: 'high' | 'medium' | 'low';
}

interface AgentOptimization {
  agent: AgentName;
  type: 'capability_enhancement' | 'performance_optimization' | 'specialization_improvement';
  currentPerformance: number;
  targetPerformance: number;
  suggestion: string;
}

interface SystemOptimization {
  type: 'api_performance' | 'api_reliability' | 'resource_optimization';
  provider?: string;
  issue: string;
  currentValue: number;
  targetValue: number;
  suggestion: string;
}

interface SessionContext {
  sessionId?: string;
  projectContext?: any;
  userBehavior?: any;
}

interface GenerationContext {
  originalPrompt: string;
  fileType: string;
  hasComponents: boolean;
  previousFailures: number;
  complexity: 'low' | 'medium' | 'high';
}

interface TaskContext {
  taskType: string;
  complexity: 'low' | 'medium' | 'high';
  priority: 'low' | 'medium' | 'high';
}

interface Task {
  type: string;
  complexity: 'low' | 'medium' | 'high';
  requirements: string[];
}

interface Recommendation {
  type: string;
  priority: 'high' | 'medium' | 'low';
  message: string;
  actionable: boolean;
  context: string;
  confidence: number;
}

interface KnowledgeEntry {
  id: string;
  type: 'success_pattern' | 'failure_pattern';
  context: string;
  successPatterns?: SuccessPattern[];
  failurePatterns?: FailurePattern[];
  confidence: number;
  lastUpdated: string;
  modification: string;
  relevanceScore?: number;
}

interface FailurePattern {
  id: string;
  context: string;
  approach: string;
  outcome: string;
  failureScore: number;
  conditions: Record<string, any>;
}

interface Context {
  [key: string]: any;
}

// Initialize and export singleton instances
export const feedbackService = FeedbackCollectionService.getInstance();
export const analyticsEngine = new AnalyticsEngine();
export const adaptiveOptimizer = new AdaptiveOptimizer();
export const learningMemory = new LearningMemory();

// Load persisted data on initialization
feedbackService.loadPersistedMetrics();
learningMemory.loadPersistedKnowledge();


