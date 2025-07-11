import React, { useState, useEffect } from 'react';
import { AIProviderFactory } from '../services/aiProviderInterface';
import { Icons } from '../constants';

interface AIProviderSelectorProps {
    currentProvider?: string;
    onProviderChange: (provider: string) => void;
    onProviderTest?: (provider: string) => Promise<boolean>;
    disabled?: boolean;
}

interface ProviderInfo {
    name: string;
    displayName: string;
    description: string;
    capabilities: string[];
    isConfigured: boolean;
    isAvailable: boolean;
}

const AIProviderSelector: React.FC<AIProviderSelectorProps> = ({
    currentProvider,
    onProviderChange,
    onProviderTest,
    disabled = false
}) => {
    const [providers, setProviders] = useState<ProviderInfo[]>([]);
    const [testingProvider, setTestingProvider] = useState<string | null>(null);
    const [testResults, setTestResults] = useState<Record<string, boolean>>({});
    const [showDetails, setShowDetails] = useState(false);

    useEffect(() => {
        loadProviders();
    }, []);

    const loadProviders = () => {
        AIProviderFactory.initialize();
        
        const allProviders = AIProviderFactory.getAllProviders();
        const availableProviders = AIProviderFactory.getAvailableProviders();
        
        const providerInfos: ProviderInfo[] = allProviders.map(name => {
            const provider = AIProviderFactory.getProvider(name);
            const capabilities = AIProviderFactory.getProviderCapabilities(name);
            
            return {
                name,
                displayName: getDisplayName(name),
                description: getDescription(name),
                capabilities,
                isConfigured: provider?.isConfigured() || false,
                isAvailable: availableProviders.includes(name)
            };
        });

        setProviders(providerInfos);
    };

    const getDisplayName = (name: string): string => {
        const displayNames: Record<string, string> = {
            'gemini': 'Google Gemini',
            'claude': 'Anthropic Claude',
            'blackbox': 'Blackbox AI'
        };
        return displayNames[name] || name.charAt(0).toUpperCase() + name.slice(1);
    };

    const getDescription = (name: string): string => {
        const descriptions: Record<string, string> = {
            'gemini': 'Google\'s multimodal AI model with strong reasoning capabilities',
            'claude': 'Anthropic\'s AI assistant focused on helpful, harmless, and honest responses',
            'blackbox': 'AI specialized in code generation and software development tasks'
        };
        return descriptions[name] || 'AI provider for text generation and assistance';
    };

    const handleProviderChange = (providerName: string) => {
        if (!disabled) {
            onProviderChange(providerName);
        }
    };

    const handleTestProvider = async (providerName: string) => {
        if (!onProviderTest || testingProvider) return;
        
        setTestingProvider(providerName);
        try {
            const result = await onProviderTest(providerName);
            setTestResults(prev => ({ ...prev, [providerName]: result }));
        } catch (error) {
            console.error(`Failed to test provider ${providerName}:`, error);
            setTestResults(prev => ({ ...prev, [providerName]: false }));
        } finally {
            setTestingProvider(null);
        }
    };

    const getStatusIcon = (provider: ProviderInfo) => {
        if (testingProvider === provider.name) {
            return (
                <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
            );
        }
        
        if (provider.name in testResults) {
            return testResults[provider.name] ? (
                <Icons.Check aria-label="Test passed" />
            ) : (
                <div className="w-4 h-4 bg-red-500 rounded-full" />
            );
        }
        
        if (provider.isAvailable) {
            return <div className="w-4 h-4 bg-green-500 rounded-full" />;
        } else if (provider.isConfigured) {
            return <div className="w-4 h-4 bg-yellow-500 rounded-full" />;
        } else {
            return <div className="w-4 h-4 bg-gray-500 rounded-full" />;
        }
    };

    const getStatusText = (provider: ProviderInfo) => {
        if (testingProvider === provider.name) {
            return 'Testing...';
        }
        
        if (provider.name in testResults) {
            return testResults[provider.name] ? 'Test Passed' : 'Test Failed';
        }
        
        if (provider.isAvailable) {
            return 'Available';
        } else if (provider.isConfigured) {
            return 'Configured';
        } else {
            return 'Not Configured';
        }
    };

    return (
        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <Icons.Cpu aria-label="AI providers" />
                    AI Providers
                </h3>
                <button
                    onClick={() => setShowDetails(!showDetails)}
                    className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400"
                    aria-pressed={showDetails}
                    aria-label="Toggle provider details"
                >
                    {showDetails ? 'Hide Details' : 'Show Details'}
                </button>
            </div>

            <div className="space-y-4">
                {providers.map(provider => (
                    <div
                        key={provider.name}
                        className={`border rounded-lg p-4 transition-all duration-200 ${
                            currentProvider === provider.name
                                ? 'border-cyan-500 bg-cyan-500/10'
                                : 'border-gray-600 hover:border-gray-500'
                        }`}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <button
                                    onClick={() => handleProviderChange(provider.name)}
                                    disabled={disabled || !provider.isAvailable}
                                    className={`w-4 h-4 rounded-full border-2 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400 ${
                                        currentProvider === provider.name
                                            ? 'bg-cyan-500 border-cyan-500'
                                            : 'border-gray-400 hover:border-cyan-400'
                                    } ${
                                        disabled || !provider.isAvailable
                                            ? 'opacity-50 cursor-not-allowed'
                                            : 'cursor-pointer'
                                    }`}
                                    aria-label={`Select ${provider.displayName}`}
                                    role="radio"
                                    aria-checked={currentProvider === provider.name}
                                />
                                
                                <div>
                                    <h4 className="text-white font-medium">{provider.displayName}</h4>
                                    <p className="text-gray-400 text-sm">{provider.description}</p>
                                </div>
                            </div>

                            <div className="flex items-center space-x-3">
                                <div className="flex items-center space-x-2">
                                    {getStatusIcon(provider)}
                                    <span className="text-sm text-gray-400">
                                        {getStatusText(provider)}
                                    </span>
                                </div>
                                
                                {onProviderTest && provider.isAvailable && (
                                    <button
                                        onClick={() => handleTestProvider(provider.name)}
                                        disabled={testingProvider !== null}
                                        className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-white rounded transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400 disabled:opacity-50"
                                        aria-label={`Test ${provider.displayName}`}
                                    >
                                        Test
                                    </button>
                                )}
                            </div>
                        </div>

                        {showDetails && (
                            <div className="mt-4 pt-4 border-t border-gray-600">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <h5 className="text-sm font-medium text-white mb-2">Capabilities</h5>
                                        <div className="flex flex-wrap gap-1">
                                            {provider.capabilities.map(capability => (
                                                <span
                                                    key={capability}
                                                    className="px-2 py-1 text-xs bg-gray-700 text-gray-300 rounded"
                                                >
                                                    {capability}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                    
                                    <div>
                                        <h5 className="text-sm font-medium text-white mb-2">Configuration</h5>
                                        <div className="text-sm text-gray-400">
                                            {provider.isConfigured ? (
                                                <span className="text-green-400">✓ API key configured</span>
                                            ) : (
                                                <span className="text-red-400">✗ API key required</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {providers.length === 0 && (
                <div className="text-center py-8">
                    <p className="text-gray-400">No AI providers available</p>
                    <p className="text-gray-500 text-sm mt-2">
                        Configure API keys to enable AI providers
                    </p>
                </div>
            )}

            <div className="mt-6 p-4 bg-gray-700/50 rounded-lg">
                <h4 className="text-sm font-medium text-white mb-2">Configuration Help</h4>
                <div className="text-sm text-gray-400 space-y-1">
                    <p>• <strong>Gemini:</strong> Set GEMINI_API_KEY environment variable</p>
                    <p>• <strong>Claude:</strong> Set CLAUDE_API_KEY or ANTHROPIC_API_KEY environment variable</p>
                    <p>• <strong>Blackbox:</strong> Set BLACKBOX_API_KEY environment variable</p>
                </div>
            </div>
        </div>
    );
};

export default AIProviderSelector;

