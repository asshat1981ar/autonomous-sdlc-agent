import React, { useState } from 'react';
import '../styles/steampunk.css';
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
export const SteampunkAgentDevelopment = ({ agents, availableModels = defaultModels, onCreateAgent, onUpdateAgent, onDeleteAgent, onTrainAgent, onTestAgent, isLoading = false }) => {
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [testPrompt, setTestPrompt] = useState('');
    const [newAgent, setNewAgent] = useState({
        name: '',
        role: '',
        model: availableModels[0] || '',
        capabilities: [],
        specializations: [],
        contextWindow: 32000,
        status: 'inactive',
        performance: { accuracy: 0, speed: 0, reasoning: 0, context: 0 }
    });
    const handleRoleSelect = (role) => {
        const template = roleTemplates[role];
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
    const getStatusIcon = (status) => {
        const icons = {
            'active': '🟢',
            'inactive': '⚫',
            'training': '🔄',
            'error': '🔴'
        };
        return icons[status] || '❓';
    };
    const getModelIcon = (model) => {
        if (model.includes('DeepSeek'))
            return '🧠';
        if (model.includes('Qwen'))
            return '💎';
        if (model.includes('Llama'))
            return '🦙';
        if (model.includes('Gemini'))
            return '💫';
        if (model.includes('Claude'))
            return '🎭';
        if (model.includes('GPT'))
            return '🤖';
        return '⚙️';
    };
    const getPerformanceColor = (score) => {
        if (score >= 80)
            return 'text-emerald-accent';
        if (score >= 60)
            return 'text-amber-glow';
        return 'text-rust-red';
    };
    const formatContextWindow = (tokens) => {
        if (tokens >= 1000000)
            return `${(tokens / 1000000).toFixed(1)}M`;
        if (tokens >= 1000)
            return `${(tokens / 1000).toFixed(0)}K`;
        return tokens.toString();
    };
    return (React.createElement("div", { className: "steampunk-panel p-6 h-full flex flex-col" },
        React.createElement("div", { className: "flex items-center gap-3 mb-6" },
            React.createElement("div", { className: "steampunk-gear" }),
            React.createElement("h3", { className: "text-xl font-bold text-white", style: { fontFamily: 'var(--heading-font)' } }, "Mechanical Mind Foundry"),
            React.createElement("div", { className: "steampunk-gear", style: { animationDirection: 'reverse' } })),
        React.createElement("div", { className: "grid grid-cols-4 gap-4 mb-6" },
            React.createElement("div", { className: "steampunk-agent-card text-center" },
                React.createElement("div", { className: "text-2xl font-bold text-emerald-accent" }, agents.filter(a => a.status === 'active').length),
                React.createElement("div", { className: "text-sm text-gray-300" }, "Active Agents")),
            React.createElement("div", { className: "steampunk-agent-card text-center" },
                React.createElement("div", { className: "text-2xl font-bold text-amber-glow" }, agents.filter(a => a.status === 'training').length),
                React.createElement("div", { className: "text-sm text-gray-300" }, "In Training")),
            React.createElement("div", { className: "steampunk-agent-card text-center" },
                React.createElement("div", { className: "text-2xl font-bold text-brass-primary" }, agents.length),
                React.createElement("div", { className: "text-sm text-gray-300" }, "Total Agents")),
            React.createElement("div", { className: "steampunk-agent-card text-center" },
                React.createElement("div", { className: "text-2xl font-bold text-steel-blue" },
                    Math.round(agents.reduce((sum, a) => sum + a.performance.accuracy, 0) / agents.length || 0),
                    "%"),
                React.createElement("div", { className: "text-sm text-gray-300" }, "Avg Performance"))),
        React.createElement("div", { className: "flex gap-3 mb-6" },
            React.createElement("button", { onClick: () => setShowCreateForm(true), className: "steampunk-button flex-1", disabled: isLoading },
                React.createElement("span", { className: "mr-2" }, "\u2697\uFE0F"),
                "Forge New Agent"),
            React.createElement("button", { onClick: () => { }, className: "steampunk-button bg-emerald-accent border-emerald-accent hover:bg-green-600", disabled: isLoading },
                React.createElement("span", { className: "mr-2" }, "\uD83C\uDFAF"),
                "Train Team")),
        showCreateForm && (React.createElement("div", { className: "steampunk-github mb-6" },
            React.createElement("h4", { className: "text-lg font-semibold text-antique-white mb-4" }, "Forge New Mechanical Mind"),
            React.createElement("div", { className: "space-y-4" },
                React.createElement("div", { className: "grid grid-cols-2 gap-4" },
                    React.createElement("div", null,
                        React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-1" }, "Agent Name"),
                        React.createElement("input", { type: "text", value: newAgent.name, onChange: (e) => setNewAgent(prev => ({ ...prev, name: e.target.value })), placeholder: "Steam-Powered Coder", className: "steampunk-input w-full" })),
                    React.createElement("div", null,
                        React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-1" }, "Base Model Engine"),
                        React.createElement("select", { value: newAgent.model, onChange: (e) => setNewAgent(prev => ({ ...prev, model: e.target.value })), className: "steampunk-input w-full bg-coal-black" }, availableModels.map(model => (React.createElement("option", { key: model, value: model },
                            getModelIcon(model),
                            " ",
                            model)))))),
                React.createElement("div", null,
                    React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-2" }, "Role Specialization"),
                    React.createElement("div", { className: "grid grid-cols-2 gap-2" }, Object.keys(roleTemplates).map(role => (React.createElement("button", { key: role, onClick: () => handleRoleSelect(role), className: `p-3 rounded-lg border-2 text-sm transition-all ${newAgent.role === role
                            ? 'border-brass-primary bg-brass-primary bg-opacity-20 text-brass-primary'
                            : 'border-gray-600 hover:border-brass-primary text-gray-300'}` }, role))))),
                newAgent.role && (React.createElement("div", null,
                    React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-1" }, "Role Description"),
                    React.createElement("p", { className: "text-sm text-gray-300 bg-coal-black p-3 rounded" }, roleTemplates[newAgent.role]?.description))),
                React.createElement("div", null,
                    React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-1" }, "Context Window (tokens)"),
                    React.createElement("input", { type: "number", value: newAgent.contextWindow, onChange: (e) => setNewAgent(prev => ({ ...prev, contextWindow: parseInt(e.target.value) || 32000 })), min: "1000", max: "200000", className: "steampunk-input w-full" })),
                React.createElement("div", { className: "flex gap-3" },
                    React.createElement("button", { onClick: handleCreateAgent, disabled: !newAgent.name || !newAgent.role || !newAgent.model || isLoading, className: "steampunk-button flex-1" }, isLoading ? React.createElement("div", { className: "steampunk-loading w-4 h-4" }) : 'Create Agent'),
                    React.createElement("button", { onClick: () => setShowCreateForm(false), className: "steampunk-button bg-gray-600 border-gray-600 hover:bg-gray-500" }, "Cancel"))))),
        React.createElement("div", { className: "flex-1 overflow-y-auto steampunk-scroll" }, agents.length === 0 ? (React.createElement("div", { className: "text-center text-gray-400 mt-8" },
            React.createElement("div", { className: "text-6xl mb-4" }, "\uD83C\uDFED"),
            React.createElement("p", null, "No mechanical minds in the foundry yet..."),
            React.createElement("p", { className: "text-sm mt-2" }, "Create your first agent to begin the revolution!"))) : (React.createElement("div", { className: "space-y-4" }, agents.map((agent) => (React.createElement("div", { key: agent.id, className: `steampunk-agent-card cursor-pointer transition-all ${selectedAgent?.id === agent.id ? 'ring-2 ring-brass-primary' : ''}`, onClick: () => setSelectedAgent(selectedAgent?.id === agent.id ? null : agent) },
            React.createElement("div", { className: "flex items-start justify-between mb-4" },
                React.createElement("div", { className: "flex items-center gap-3" },
                    React.createElement("div", { className: "text-2xl" }, getModelIcon(agent.model)),
                    React.createElement("div", null,
                        React.createElement("h4", { className: "font-semibold text-antique-white flex items-center gap-2" },
                            agent.name,
                            React.createElement("span", { className: "text-sm" }, getStatusIcon(agent.status))),
                        React.createElement("p", { className: "text-sm text-brass-primary" }, agent.role),
                        React.createElement("p", { className: "text-xs text-gray-400" }, agent.model))),
                React.createElement("div", { className: "text-right" },
                    React.createElement("div", { className: "text-xs text-gray-400" },
                        "Context: ",
                        formatContextWindow(agent.contextWindow)),
                    React.createElement("div", { className: "text-xs text-gray-400" },
                        "Last active: ",
                        agent.lastActive.toLocaleDateString()))),
            React.createElement("div", { className: "grid grid-cols-4 gap-3 mb-4" },
                React.createElement("div", { className: "text-center" },
                    React.createElement("div", { className: `text-lg font-bold ${getPerformanceColor(agent.performance.accuracy)}` },
                        agent.performance.accuracy,
                        "%"),
                    React.createElement("div", { className: "text-xs text-gray-400" }, "Accuracy")),
                React.createElement("div", { className: "text-center" },
                    React.createElement("div", { className: `text-lg font-bold ${getPerformanceColor(agent.performance.speed)}` },
                        agent.performance.speed,
                        "%"),
                    React.createElement("div", { className: "text-xs text-gray-400" }, "Speed")),
                React.createElement("div", { className: "text-center" },
                    React.createElement("div", { className: `text-lg font-bold ${getPerformanceColor(agent.performance.reasoning)}` },
                        agent.performance.reasoning,
                        "%"),
                    React.createElement("div", { className: "text-xs text-gray-400" }, "Reasoning")),
                React.createElement("div", { className: "text-center" },
                    React.createElement("div", { className: `text-lg font-bold ${getPerformanceColor(agent.performance.context)}` },
                        agent.performance.context,
                        "%"),
                    React.createElement("div", { className: "text-xs text-gray-400" }, "Context"))),
            React.createElement("div", { className: "mb-4" },
                React.createElement("div", { className: "flex flex-wrap gap-1 mb-2" }, agent.capabilities.map(cap => (React.createElement("span", { key: cap, className: "text-xs bg-steel-blue bg-opacity-30 px-2 py-1 rounded" }, cap)))),
                React.createElement("div", { className: "flex flex-wrap gap-1" }, agent.specializations.map(spec => (React.createElement("span", { key: spec, className: "text-xs bg-brass-primary bg-opacity-30 px-2 py-1 rounded" }, spec))))),
            selectedAgent?.id === agent.id && (React.createElement("div", { className: "border-t border-brass-primary pt-4 mt-4" },
                React.createElement("div", { className: "grid grid-cols-2 gap-4 mb-4" },
                    React.createElement("div", null,
                        React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-1" }, "Test Agent"),
                        React.createElement("div", { className: "flex gap-2" },
                            React.createElement("input", { type: "text", value: testPrompt, onChange: (e) => setTestPrompt(e.target.value), placeholder: "Write a function to sort an array...", className: "steampunk-input flex-1 text-sm" }),
                            React.createElement("button", { onClick: () => {
                                    if (testPrompt.trim()) {
                                        onTestAgent(agent.id, testPrompt);
                                        setTestPrompt('');
                                    }
                                }, className: "steampunk-button px-3 py-1 text-sm", disabled: !testPrompt.trim() || isLoading }, "\uD83E\uDDEA Test"))),
                    React.createElement("div", { className: "flex gap-2" },
                        React.createElement("button", { onClick: () => onTrainAgent(agent.id, {}), className: "steampunk-button flex-1 text-sm bg-emerald-accent border-emerald-accent hover:bg-green-600", disabled: isLoading }, "\uD83C\uDFAF Train"),
                        React.createElement("button", { onClick: () => onDeleteAgent(agent.id), className: "steampunk-button text-sm bg-rust-red border-rust-red hover:bg-red-600" }, "\uD83D\uDDD1\uFE0F")))))))))))));
};
export default SteampunkAgentDevelopment;
