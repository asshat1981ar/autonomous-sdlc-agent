import React, { useState, useCallback } from 'react';
import '../styles/steampunk.css';

interface AgentConfig {
  id: string;
  name: string;
  role: string;
  model: string;
  capabilities: string[];
  status: 'active' | 'inactive' | 'training' | 'error';
  performance: {
    accuracy: number;
    speed: number;
    reasoning: number;
    context: number;
  };
  contextWindow: number;
  specializations: string[];
  lastActive: Date;
}

interface AgentDevelopmentProps {
  agents: AgentConfig[];
  availableModels: string[];
  onCreateAgent: (config: Omit<AgentConfig, 'id' | 'lastActive'>) => void;
  onUpdateAgent: (id: string, config: Partial<AgentConfig>) => void;
  onDeleteAgent: (id: string) => void;
  onTrainAgent: (id: string, trainingData: any) => void;
  onTestAgent: (id: string, testPrompt: string) => void;
  isLoading?: boolean;
}

const defaultModels = [
  'DeepSeek-V3-671B',
  'DeepSeek-R1-Distill-70B',
  'Qwen-2.5-Coder-32B',
  'DeepCoder-14B',
  'Llama-3.3-70B-Instruct',
  'Gemini-2.0-Flash',
  'GLM-Z1-32B',
  'Qwerky-72B',
  'Claude-3.5-Sonnet',
  'GPT-4-Turbo',
  'Mistral-24B-Instruct'
];

const roleTemplates = {
  'Project Planner': {
    description: 'Oversees project architecture and task coordination',
    capabilities: ['planning', 'coordination', 'requirements_analysis'],
    specializations: ['architecture', 'task_breakdown', 'project_management']
  },
  'Code Generator': {
    description: 'Implements code from specifications',
    capabilities: ['code_generation', 'implementation', 'syntax_optimization'],
    specializations: ['frontend', 'backend', 'algorithms', 'optimization']
  },
  'Code Reviewer': {
    description: 'Reviews code for quality and correctness',
    capabilities: ['code_review', 'debugging', 'testing', 'security_analysis'],
    specializations: ['quality_assurance', 'security', 'performance', 'best_practices']
  },
  'Documentation Agent': {
    description: 'Creates and maintains project documentation',
    capabilities: ['documentation', 'explanation', 'communication'],
    specializations: ['technical_writing', 'api_docs', 'user_guides', 'multilingual']
  },
  'Visual Agent': {
    description: 'Processes visual inputs and UI/UX tasks',
    capabilities: ['vision', 'ui_analysis', 'design_interpretation'],
    specializations: ['ui_generation', 'image_analysis', 'design_patterns']
  }
};

export const SteampunkAgentDevelopment: React.FC<AgentDevelopmentProps> = ({
  agents,
  availableModels = defaultModels,
  onCreateAgent,
  onUpdateAgent,
  onDeleteAgent,
  onTrainAgent,
  onTestAgent,
  isLoading = false
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentConfig | null>(null);
  const [testPrompt, setTestPrompt] = useState('');
  const [newAgent, setNewAgent] = useState({
    name: '',
    role: '',
    model: availableModels[0] || '',
    capabilities: [] as string[],
    specializations: [] as string[],
    contextWindow: 32000,
    status: 'inactive' as const,
    performance: { accuracy: 0, speed: 0, reasoning: 0, context: 0 }
  });

  const handleRoleSelect = (role: string) => {
    const template = roleTemplates[role as keyof typeof roleTemplates];
    if (template) {
      setNewAgent(prev => ({
        ...prev,
        role,
        capabilities: [...template.capabilities],
        specializations: [...template.specializations]
      }));
    }
  };

  const handleCreateAgent = () => {
    if (newAgent.name && newAgent.role && newAgent.model) {
      onCreateAgent(newAgent);
      setNewAgent({
        name: '',
        role: '',
        model: availableModels[0] || '',
        capabilities: [],
        specializations: [],
        contextWindow: 32000,
        status: 'inactive',
        performance: { accuracy: 0, speed: 0, reasoning: 0, context: 0 }
      });
      setShowCreateForm(false);
    }
  };

  const getStatusIcon = (status: string) => {
    const icons = {
      'active': '🟢',
      'inactive': '⚫',
      'training': '🔄',
      'error': '🔴'
    };
    return icons[status as keyof typeof icons] || '❓';
  };

  const getModelIcon = (model: string) => {
    if (model.includes('DeepSeek')) return '🧠';
    if (model.includes('Qwen')) return '💎';
    if (model.includes('Llama')) return '🦙';
    if (model.includes('Gemini')) return '💫';
    if (model.includes('Claude')) return '🎭';
    if (model.includes('GPT')) return '🤖';
    return '⚙️';
  };

  const getPerformanceColor = (score: number) => {
    if (score >= 80) return 'text-emerald-accent';
    if (score >= 60) return 'text-amber-glow';
    return 'text-rust-red';
  };

  const formatContextWindow = (tokens: number) => {
    if (tokens >= 1000000) return `${(tokens / 1000000).toFixed(1)}M`;
    if (tokens >= 1000) return `${(tokens / 1000).toFixed(0)}K`;
    return tokens.toString();
  };

  return (
    <div className="steampunk-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="steampunk-gear"></div>
        <h3 className="text-xl font-bold text-white" style={{ fontFamily: 'var(--heading-font)' }}>
          Mechanical Mind Foundry
        </h3>
        <div className="steampunk-gear" style={{ animationDirection: 'reverse' }}></div>
      </div>

      {/* Agent Statistics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="steampunk-agent-card text-center">
          <div className="text-2xl font-bold text-emerald-accent">
            {agents.filter(a => a.status === 'active').length}
          </div>
          <div className="text-sm text-gray-300">Active Agents</div>
        </div>
        <div className="steampunk-agent-card text-center">
          <div className="text-2xl font-bold text-amber-glow">
            {agents.filter(a => a.status === 'training').length}
          </div>
          <div className="text-sm text-gray-300">In Training</div>
        </div>
        <div className="steampunk-agent-card text-center">
          <div className="text-2xl font-bold text-brass-primary">
            {agents.length}
          </div>
          <div className="text-sm text-gray-300">Total Agents</div>
        </div>
        <div className="steampunk-agent-card text-center">
          <div className="text-2xl font-bold text-steel-blue">
            {Math.round(agents.reduce((sum, a) => sum + a.performance.accuracy, 0) / agents.length || 0)}%
          </div>
          <div className="text-sm text-gray-300">Avg Performance</div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={() => setShowCreateForm(true)}
          className="steampunk-button flex-1"
          disabled={isLoading}
        >
          <span className="mr-2">⚗️</span>
          Forge New Agent
        </button>
        
        <button
          onClick={() => {/* TODO: Implement team training */}}
          className="steampunk-button bg-emerald-accent border-emerald-accent hover:bg-green-600"
          disabled={isLoading}
        >
          <span className="mr-2">🎯</span>
          Train Team
        </button>
      </div>

      {/* Create Agent Form */}
      {showCreateForm && (
        <div className="steampunk-github mb-6">
          <h4 className="text-lg font-semibold text-antique-white mb-4">
            Forge New Mechanical Mind
          </h4>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-antique-white mb-1">
                  Agent Name
                </label>
                <input
                  type="text"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Steam-Powered Coder"
                  className="steampunk-input w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-antique-white mb-1">
                  Base Model Engine
                </label>
                <select
                  value={newAgent.model}
                  onChange={(e) => setNewAgent(prev => ({ ...prev, model: e.target.value }))}
                  className="steampunk-input w-full bg-coal-black"
                >
                  {availableModels.map(model => (
                    <option key={model} value={model}>
                      {getModelIcon(model)} {model}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-antique-white mb-2">
                Role Specialization
              </label>
              <div className="grid grid-cols-2 gap-2">
                {Object.keys(roleTemplates).map(role => (
                  <button
                    key={role}
                    onClick={() => handleRoleSelect(role)}
                    className={`p-3 rounded-lg border-2 text-sm transition-all ${
                      newAgent.role === role
                        ? 'border-brass-primary bg-brass-primary bg-opacity-20 text-brass-primary'
                        : 'border-gray-600 hover:border-brass-primary text-gray-300'
                    }`}
                  >
                    {role}
                  </button>
                ))}
              </div>
            </div>
            
            {newAgent.role && (
              <div>
                <label className="block text-sm font-medium text-antique-white mb-1">
                  Role Description
                </label>
                <p className="text-sm text-gray-300 bg-coal-black p-3 rounded">
                  {roleTemplates[newAgent.role as keyof typeof roleTemplates]?.description}
                </p>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-antique-white mb-1">
                Context Window (tokens)
              </label>
              <input
                type="number"
                value={newAgent.contextWindow}
                onChange={(e) => setNewAgent(prev => ({ ...prev, contextWindow: parseInt(e.target.value) || 32000 }))}
                min="1000"
                max="200000"
                className="steampunk-input w-full"
              />
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={handleCreateAgent}
                disabled={!newAgent.name || !newAgent.role || !newAgent.model || isLoading}
                className="steampunk-button flex-1"
              >
                {isLoading ? <div className="steampunk-loading w-4 h-4"></div> : 'Create Agent'}
              </button>
              <button
                onClick={() => setShowCreateForm(false)}
                className="steampunk-button bg-gray-600 border-gray-600 hover:bg-gray-500"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Agents List */}
      <div className="flex-1 overflow-y-auto steampunk-scroll">
        {agents.length === 0 ? (
          <div className="text-center text-gray-400 mt-8">
            <div className="text-6xl mb-4">🏭</div>
            <p>No mechanical minds in the foundry yet...</p>
            <p className="text-sm mt-2">Create your first agent to begin the revolution!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className={`steampunk-agent-card cursor-pointer transition-all ${
                  selectedAgent?.id === agent.id ? 'ring-2 ring-brass-primary' : ''
                }`}
                onClick={() => setSelectedAgent(selectedAgent?.id === agent.id ? null : agent)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="text-2xl">{getModelIcon(agent.model)}</div>
                    <div>
                      <h4 className="font-semibold text-antique-white flex items-center gap-2">
                        {agent.name}
                        <span className="text-sm">{getStatusIcon(agent.status)}</span>
                      </h4>
                      <p className="text-sm text-brass-primary">{agent.role}</p>
                      <p className="text-xs text-gray-400">{agent.model}</p>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-xs text-gray-400">
                      Context: {formatContextWindow(agent.contextWindow)}
                    </div>
                    <div className="text-xs text-gray-400">
                      Last active: {agent.lastActive.toLocaleDateString()}
                    </div>
                  </div>
                </div>
                
                {/* Performance Metrics */}
                <div className="grid grid-cols-4 gap-3 mb-4">
                  <div className="text-center">
                    <div className={`text-lg font-bold ${getPerformanceColor(agent.performance.accuracy)}`}>
                      {agent.performance.accuracy}%
                    </div>
                    <div className="text-xs text-gray-400">Accuracy</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-lg font-bold ${getPerformanceColor(agent.performance.speed)}`}>
                      {agent.performance.speed}%
                    </div>
                    <div className="text-xs text-gray-400">Speed</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-lg font-bold ${getPerformanceColor(agent.performance.reasoning)}`}>
                      {agent.performance.reasoning}%
                    </div>
                    <div className="text-xs text-gray-400">Reasoning</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-lg font-bold ${getPerformanceColor(agent.performance.context)}`}>
                      {agent.performance.context}%
                    </div>
                    <div className="text-xs text-gray-400">Context</div>
                  </div>
                </div>
                
                {/* Capabilities & Specializations */}
                <div className="mb-4">
                  <div className="flex flex-wrap gap-1 mb-2">
                    {agent.capabilities.map(cap => (
                      <span key={cap} className="text-xs bg-steel-blue bg-opacity-30 px-2 py-1 rounded">
                        {cap}
                      </span>
                    ))}
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {agent.specializations.map(spec => (
                      <span key={spec} className="text-xs bg-brass-primary bg-opacity-30 px-2 py-1 rounded">
                        {spec}
                      </span>
                    ))}
                  </div>
                </div>
                
                {/* Expanded Details */}
                {selectedAgent?.id === agent.id && (
                  <div className="border-t border-brass-primary pt-4 mt-4">
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-antique-white mb-1">
                          Test Agent
                        </label>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={testPrompt}
                            onChange={(e) => setTestPrompt(e.target.value)}
                            placeholder="Write a function to sort an array..."
                            className="steampunk-input flex-1 text-sm"
                          />
                          <button
                            onClick={() => {
                              if (testPrompt.trim()) {
                                onTestAgent(agent.id, testPrompt);
                                setTestPrompt('');
                              }
                            }}
                            className="steampunk-button px-3 py-1 text-sm"
                            disabled={!testPrompt.trim() || isLoading}
                          >
                            🧪 Test
                          </button>
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <button
                          onClick={() => onTrainAgent(agent.id, {})}
                          className="steampunk-button flex-1 text-sm bg-emerald-accent border-emerald-accent hover:bg-green-600"
                          disabled={isLoading}
                        >
                          🎯 Train
                        </button>
                        <button
                          onClick={() => onDeleteAgent(agent.id)}
                          className="steampunk-button text-sm bg-rust-red border-rust-red hover:bg-red-600"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SteampunkAgentDevelopment;