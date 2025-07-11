import React, { useState } from 'react';
import { Icons } from '../constants';

interface AIInteraction {
    id: string;
    timestamp: string;
    persona: string;
    prompt: string;
    response: string;
    model: string;
    temperature: number;
    reasoning?: string;
}

interface AITransparencyPanelProps {
    interactions: AIInteraction[];
    currentPersona?: string;
    onPersonaChange?: (persona: string) => void;
    onParameterChange?: (parameter: string, value: any) => void;
    aiParameters?: {
        temperature: number;
        maxTokens: number;
        topP: number;
    };
}

const AITransparencyPanel: React.FC<AITransparencyPanelProps> = ({
    interactions,
    currentPersona = 'Orchestrator',
    onPersonaChange,
    onParameterChange,
    aiParameters = { temperature: 0.7, maxTokens: 2048, topP: 0.9 }
}) => {
    const [selectedInteraction, setSelectedInteraction] = useState<string | null>(null);
    const [showPrompts, setShowPrompts] = useState(false);
    const [showParameters, setShowParameters] = useState(false);

    const personas = [
        { name: 'Orchestrator', description: 'Coordinates the overall development process' },
        { name: 'Market Analyst', description: 'Analyzes market trends and competition' },
        { name: 'Product Strategist', description: 'Defines product strategy and features' },
        { name: 'Software Architect', description: 'Designs system architecture and tech stack' },
        { name: 'Frontend Expert', description: 'Specializes in UI/UX and frontend development' },
        { name: 'Backend Expert', description: 'Focuses on server-side logic and APIs' },
        { name: 'QA Engineer', description: 'Ensures code quality and testing' },
        { name: 'DevOps Engineer', description: 'Handles deployment and infrastructure' }
    ];

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleString();
    };

    const truncateText = (text: string, maxLength: number) => {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    };

    return (
        <div className="bg-gray-800/50 border border-gray-700 rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    <Icons.Eye aria-label="AI transparency" />
                    AI Transparency
                </h3>
                <div className="flex space-x-2">
                    <button
                        onClick={() => setShowPrompts(!showPrompts)}
                        className={`px-3 py-1 text-sm rounded transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400 ${
                            showPrompts 
                                ? 'bg-cyan-600 text-white' 
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                        aria-pressed={showPrompts}
                        aria-label="Toggle prompt visibility"
                    >
                        Show Prompts
                    </button>
                    <button
                        onClick={() => setShowParameters(!showParameters)}
                        className={`px-3 py-1 text-sm rounded transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400 ${
                            showParameters 
                                ? 'bg-cyan-600 text-white' 
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                        aria-pressed={showParameters}
                        aria-label="Toggle parameter controls"
                    >
                        Parameters
                    </button>
                </div>
            </div>

            {/* Current Persona Info */}
            <div className="mb-6 p-4 bg-gray-700/50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                    <h4 className="text-lg font-semibold text-white">Current AI Persona</h4>
                    {onPersonaChange && (
                        <select
                            value={currentPersona}
                            onChange={(e) => onPersonaChange(e.target.value)}
                            className="bg-gray-600 text-white rounded px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400"
                            aria-label="Select AI persona"
                        >
                            {personas.map(persona => (
                                <option key={persona.name} value={persona.name}>
                                    {persona.name}
                                </option>
                            ))}
                        </select>
                    )}
                </div>
                <p className="text-gray-300 text-sm">
                    {personas.find(p => p.name === currentPersona)?.description}
                </p>
            </div>

            {/* AI Parameters */}
            {showParameters && onParameterChange && (
                <div className="mb-6 p-4 bg-gray-700/50 rounded-lg">
                    <h4 className="text-lg font-semibold text-white mb-4">AI Parameters</h4>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-300 mb-2">
                                Temperature: {aiParameters.temperature}
                            </label>
                            <input
                                type="range"
                                min="0"
                                max="2"
                                step="0.1"
                                value={aiParameters.temperature}
                                onChange={(e) => onParameterChange('temperature', parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                                aria-label="AI temperature parameter"
                            />
                            <div className="flex justify-between text-xs text-gray-400 mt-1">
                                <span>Conservative</span>
                                <span>Creative</span>
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-sm text-gray-300 mb-2">
                                Max Tokens: {aiParameters.maxTokens}
                            </label>
                            <input
                                type="range"
                                min="256"
                                max="4096"
                                step="256"
                                value={aiParameters.maxTokens}
                                onChange={(e) => onParameterChange('maxTokens', parseInt(e.target.value))}
                                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                                aria-label="Maximum tokens parameter"
                            />
                        </div>

                        <div>
                            <label className="block text-sm text-gray-300 mb-2">
                                Top P: {aiParameters.topP}
                            </label>
                            <input
                                type="range"
                                min="0.1"
                                max="1"
                                step="0.1"
                                value={aiParameters.topP}
                                onChange={(e) => onParameterChange('topP', parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                                aria-label="Top P parameter"
                            />
                        </div>
                    </div>
                </div>
            )}

            {/* Recent AI Interactions */}
            <div>
                <h4 className="text-lg font-semibold text-white mb-4">Recent AI Interactions</h4>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                    {interactions.length === 0 ? (
                        <p className="text-gray-400 text-sm">No AI interactions yet.</p>
                    ) : (
                        interactions.map((interaction) => (
                            <div
                                key={interaction.id}
                                className="border border-gray-600 rounded-lg p-3 hover:border-gray-500 transition-colors cursor-pointer"
                                onClick={() => setSelectedInteraction(
                                    selectedInteraction === interaction.id ? null : interaction.id
                                )}
                                role="button"
                                tabIndex={0}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter' || e.key === ' ') {
                                        setSelectedInteraction(
                                            selectedInteraction === interaction.id ? null : interaction.id
                                        );
                                    }
                                }}
                                aria-expanded={selectedInteraction === interaction.id}
                                aria-label={`AI interaction with ${interaction.persona} at ${formatTimestamp(interaction.timestamp)}`}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-2">
                                        <span className="text-cyan-400 font-medium text-sm">
                                            {interaction.persona}
                                        </span>
                                        <span className="text-gray-500 text-xs">
                                            {formatTimestamp(interaction.timestamp)}
                                        </span>
                                    </div>
                                    <div className="flex items-center space-x-2 text-xs text-gray-400">
                                        <span>{interaction.model}</span>
                                        <span>T:{interaction.temperature}</span>
                                    </div>
                                </div>
                                
                                <div className="text-gray-300 text-sm">
                                    {truncateText(interaction.response, 100)}
                                </div>

                                {selectedInteraction === interaction.id && (
                                    <div className="mt-4 space-y-3 border-t border-gray-600 pt-3">
                                        {showPrompts && (
                                            <div>
                                                <h5 className="text-sm font-medium text-white mb-2">Prompt:</h5>
                                                <pre className="text-xs text-gray-300 bg-gray-800 p-2 rounded overflow-x-auto whitespace-pre-wrap">
                                                    {interaction.prompt}
                                                </pre>
                                            </div>
                                        )}
                                        
                                        <div>
                                            <h5 className="text-sm font-medium text-white mb-2">Full Response:</h5>
                                            <div className="text-sm text-gray-300 bg-gray-800 p-2 rounded max-h-40 overflow-y-auto">
                                                {interaction.response}
                                            </div>
                                        </div>

                                        {interaction.reasoning && (
                                            <div>
                                                <h5 className="text-sm font-medium text-white mb-2">AI Reasoning:</h5>
                                                <div className="text-sm text-gray-300 bg-gray-800 p-2 rounded">
                                                    {interaction.reasoning}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AITransparencyPanel;

