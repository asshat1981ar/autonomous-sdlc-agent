import React, { useState, useEffect, useCallback } from 'react';
import SteampunkFileUpload from './SteampunkFileUpload';
import SteampunkChatInterface from './SteampunkChatInterface';
import SteampunkGitHubIntegration from './SteampunkGitHubIntegration';
import SteampunkAgentDevelopment from './SteampunkAgentDevelopment';
import '../styles/steampunk.css';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai' | 'system';
  timestamp: Date;
  aiProvider?: string;
  attachments?: File[];
}

interface Repository {
  id: string;
  name: string;
  description: string;
  private: boolean;
  language: string;
  stars: number;
  forks: number;
  updatedAt: string;
  url: string;
  defaultBranch: string;
}

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

export const SteampunkApp: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'chat' | 'files' | 'github' | 'agents'>('chat');
  const [messages, setMessages] = useState<Message[]>([]);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [selectedRepository, setSelectedRepository] = useState<Repository | undefined>();
  const [isGitHubConnected, setIsGitHubConnected] = useState(false);
  const [selectedAIProvider, setSelectedAIProvider] = useState('Claude');
  const [isLoading, setIsLoading] = useState(false);
  const [steamPressure, setSteamPressure] = useState(75); // Fun steampunk element

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: '1',
      content: `Welcome to the Mechanical Intelligence Console! 

I am your steampunk-powered AI assistant, ready to help you with:
🔧 Code generation and analysis
⚙️ Project development and planning  
📚 Documentation and explanations
🔍 Debugging and optimization
🚀 GitHub repository management
🤖 AI agent development and coordination

Upload your blueprints, connect your repositories, and let's build something magnificent together!`,
      sender: 'ai',
      timestamp: new Date(),
      aiProvider: 'Claude'
    };
    setMessages([welcomeMessage]);

    // Initialize sample agents
    const sampleAgents: AgentConfig[] = [
      {
        id: '1',
        name: 'Steam-Powered Architect',
        role: 'Project Planner',
        model: 'DeepSeek-V3-671B',
        capabilities: ['planning', 'coordination', 'requirements_analysis'],
        status: 'active',
        performance: { accuracy: 92, speed: 75, reasoning: 95, context: 88 },
        contextWindow: 160000,
        specializations: ['architecture', 'task_breakdown', 'project_management'],
        lastActive: new Date()
      },
      {
        id: '2',
        name: 'Copper-Coil Coder',
        role: 'Code Generator',
        model: 'Qwen-2.5-Coder-32B',
        capabilities: ['code_generation', 'implementation', 'syntax_optimization'],
        status: 'active',
        performance: { accuracy: 89, speed: 92, reasoning: 85, context: 78 },
        contextWindow: 32000,
        specializations: ['frontend', 'backend', 'algorithms', 'optimization'],
        lastActive: new Date()
      }
    ];
    setAgents(sampleAgents);

    // Steam pressure animation
    const interval = setInterval(() => {
      setSteamPressure(prev => {
        const variation = Math.random() * 10 - 5; // ±5
        return Math.max(60, Math.min(95, prev + variation));
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = useCallback(async (content: string, attachments?: File[]) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date(),
      attachments
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Simulate AI response delay
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: `I understand you want to: "${content}"\n\n` +
                `Let me analyze this request using my mechanical neural networks...\n\n` +
                `Based on the current steam pressure (${steamPressure.toFixed(1)}%) and active agent configurations, I recommend:\n\n` +
                `• Engaging the ${agents.find(a => a.status === 'active')?.name || 'Steam-Powered Architect'} for project planning\n` +
                `• Utilizing ${selectedAIProvider} for detailed analysis\n` +
                `• ${attachments?.length ? `Processing ${attachments.length} attached blueprint(s)` : 'Ready to proceed without additional blueprints'}\n\n` +
                `Would you like me to proceed with this magnificent endeavor?`,
        sender: 'ai',
        timestamp: new Date(),
        aiProvider: selectedAIProvider
      };

      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  }, [selectedAIProvider, steamPressure, agents]);

  const handleFileUpload = useCallback((files: File[]) => {
    const systemMessage: Message = {
      id: Date.now().toString(),
      content: `📄 ${files.length} blueprint(s) uploaded to the mechanical archive:\n\n` +
               files.map(f => `• ${f.name} (${(f.size / 1024).toFixed(1)} KB)`).join('\n') +
               '\n\nThese documents are now available for analysis by all active agents.',
      sender: 'system',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, systemMessage]);
  }, []);

  const handleGitHubConnect = useCallback((token: string) => {
    setIsLoading(true);
    // Simulate connection delay
    setTimeout(() => {
      setIsGitHubConnected(true);
      
      // Simulate fetching repositories
      const sampleRepos: Repository[] = [
        {
          id: '1',
          name: 'steampunk-calculator',
          description: 'A brass-plated computational engine',
          private: false,
          language: 'TypeScript',
          stars: 42,
          forks: 7,
          updatedAt: '2024-01-15T10:30:00Z',
          url: 'https://github.com/user/steampunk-calculator',
          defaultBranch: 'main'
        },
        {
          id: '2',
          name: 'mechanical-mind-api',
          description: 'Backend cogitation services',
          private: true,
          language: 'Python',
          stars: 18,
          forks: 3,
          updatedAt: '2024-01-10T14:20:00Z',
          url: 'https://github.com/user/mechanical-mind-api',
          defaultBranch: 'main'
        }
      ];
      
      setRepositories(sampleRepos);
      setIsLoading(false);

      const connectMessage: Message = {
        id: Date.now().toString(),
        content: `🔗 Successfully connected to GitHub Arsenal!\n\nDiscovered ${sampleRepos.length} repositories in your mechanical vault. You can now sync, analyze, and enhance your codebases through the Repository Vault tab.`,
        sender: 'system',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, connectMessage]);
    }, 2000);
  }, []);

  const handleCreateAgent = useCallback((config: Omit<AgentConfig, 'id' | 'lastActive'>) => {
    const newAgent: AgentConfig = {
      ...config,
      id: Date.now().toString(),
      lastActive: new Date()
    };
    
    setAgents(prev => [...prev, newAgent]);

    const agentMessage: Message = {
      id: Date.now().toString(),
      content: `⚗️ New mechanical mind forged successfully!\n\n**${newAgent.name}** has been created with the following specifications:\n• Role: ${newAgent.role}\n• Engine: ${newAgent.model}\n• Context Capacity: ${(newAgent.contextWindow / 1000).toFixed(0)}K tokens\n• Specializations: ${newAgent.specializations.join(', ')}\n\nThe agent is now ready for deployment in your coding endeavors!`,
      sender: 'system',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, agentMessage]);
  }, []);

  const getTabIcon = (tab: string) => {
    const icons = {
      chat: '💬',
      files: '📁',
      github: '🔗',
      agents: '🤖'
    };
    return icons[tab as keyof typeof icons] || '⚙️';
  };

  const getTabLabel = (tab: string) => {
    const labels = {
      chat: 'Intelligence Console',
      files: 'Blueprint Archive',
      github: 'Repository Vault',
      agents: 'Mind Foundry'
    };
    return labels[tab as keyof typeof labels] || tab;
  };

  return (
    <div className="steampunk-container min-h-screen">
      {/* Header */}
      <header className="bg-gradient-to-r from-coal-black to-gray-800 border-b-2 border-brass-primary p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="steampunk-gear text-2xl"></div>
            <div>
              <h1 className="text-2xl font-bold text-antique-white" style={{ fontFamily: 'var(--heading-font)' }}>
                Autonomous SDLC Mechanica
              </h1>
              <p className="text-sm text-brass-primary">Industrial-Grade AI Development Console</p>
            </div>
          </div>
          
          {/* Steam Pressure Gauge */}
          <div className="flex items-center gap-4">
            <div className="steampunk-agent-card px-4 py-2">
              <div className="text-center">
                <div className="text-lg font-bold text-amber-glow">
                  {steamPressure.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-400">Steam Pressure</div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-sm text-antique-white">Active Agents:</span>
              <span className="text-brass-primary font-bold">
                {agents.filter(a => a.status === 'active').length}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-coal-black border-b border-brass-primary">
        <div className="flex">
          {(['chat', 'files', 'github', 'agents'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex items-center gap-2 px-6 py-4 border-r border-brass-primary transition-all ${
                activeTab === tab
                  ? 'bg-brass-gradient text-coal-black'
                  : 'text-antique-white hover:bg-brass-primary hover:bg-opacity-20'
              }`}
              style={{ fontFamily: 'var(--heading-font)' }}
            >
              <span className="text-lg">{getTabIcon(tab)}</span>
              {getTabLabel(tab)}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1">
        {activeTab === 'chat' && (
          <div className="h-screen">
            <SteampunkChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              selectedProvider={selectedAIProvider}
              onProviderChange={setSelectedAIProvider}
              availableProviders={['Claude', 'GPT-4', 'Gemini', 'DeepSeek', 'Qwen']}
            />
          </div>
        )}

        {activeTab === 'files' && (
          <div className="p-6">
            <SteampunkFileUpload
              onFileUpload={handleFileUpload}
              acceptedTypes={['.js', '.ts', '.tsx', '.py', '.md', '.json', '.txt', '.csv']}
              maxFiles={20}
              maxSize={100}
            />
          </div>
        )}

        {activeTab === 'github' && (
          <div className="h-screen">
            <SteampunkGitHubIntegration
              repositories={repositories}
              isConnected={isGitHubConnected}
              onConnect={handleGitHubConnect}
              onDisconnect={() => {
                setIsGitHubConnected(false);
                setRepositories([]);
                setSelectedRepository(undefined);
              }}
              onSelectRepository={setSelectedRepository}
              onCreateRepository={(name, description, isPrivate) => {
                console.log('Create repo:', { name, description, isPrivate });
              }}
              onSyncRepository={(repoId) => {
                console.log('Sync repo:', repoId);
              }}
              isLoading={isLoading}
              selectedRepository={selectedRepository}
            />
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="h-screen">
            <SteampunkAgentDevelopment
              agents={agents}
              availableModels={[
                'DeepSeek-V3-671B',
                'DeepSeek-R1-Distill-70B',
                'Qwen-2.5-Coder-32B',
                'DeepCoder-14B',
                'Llama-3.3-70B-Instruct',
                'Gemini-2.0-Flash',
                'GLM-Z1-32B',
                'Qwerky-72B',
                'Claude-3.5-Sonnet',
                'GPT-4-Turbo'
              ]}
              onCreateAgent={handleCreateAgent}
              onUpdateAgent={(id, config) => {
                setAgents(prev => prev.map(a => a.id === id ? { ...a, ...config } : a));
              }}
              onDeleteAgent={(id) => {
                setAgents(prev => prev.filter(a => a.id !== id));
              }}
              onTrainAgent={(id, trainingData) => {
                console.log('Train agent:', id, trainingData);
              }}
              onTestAgent={(id, testPrompt) => {
                console.log('Test agent:', id, testPrompt);
              }}
              isLoading={isLoading}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-coal-black border-t border-brass-primary p-4">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div className="flex items-center gap-4">
            <span>Powered by Steam & Silicon</span>
            <div className="w-2 h-2 bg-emerald-accent rounded-full animate-pulse"></div>
            <span>System Operational</span>
          </div>
          
          <div className="flex items-center gap-6">
            <span>Memory Cores: {agents.length}/10</span>
            <span>Pressure: {steamPressure.toFixed(1)}%</span>
            <span>Version: Mechanica v2.1.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default SteampunkApp;