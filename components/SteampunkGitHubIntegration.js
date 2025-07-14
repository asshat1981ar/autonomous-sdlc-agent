import React, { useState } from 'react';
import '../styles/steampunk.css';
export const SteampunkGitHubIntegration = ({ repositories, isConnected, onConnect, onDisconnect, onSelectRepository, onCreateRepository, onSyncRepository, isLoading = false, selectedRepository }) => {
    const [showConnectionForm, setShowConnectionForm] = useState(false);
    const [githubToken, setGithubToken] = useState('');
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [newRepoName, setNewRepoName] = useState('');
    const [newRepoDescription, setNewRepoDescription] = useState('');
    const [newRepoPrivate, setNewRepoPrivate] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const filteredRepositories = repositories.filter(repo => repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        repo.description?.toLowerCase().includes(searchTerm.toLowerCase()));
    const handleConnect = () => {
        if (githubToken.trim()) {
            onConnect(githubToken.trim());
            setGithubToken('');
            setShowConnectionForm(false);
        }
    };
    const handleCreateRepo = () => {
        if (newRepoName.trim()) {
            onCreateRepository(newRepoName.trim(), newRepoDescription.trim(), newRepoPrivate);
            setNewRepoName('');
            setNewRepoDescription('');
            setNewRepoPrivate(false);
            setShowCreateForm(false);
        }
    };
    const getLanguageIcon = (language) => {
        const icons = {
            'JavaScript': '🟨',
            'TypeScript': '🔷',
            'Python': '🐍',
            'Java': '☕',
            'C++': '⚙️',
            'Go': '🐹',
            'Rust': '🦀',
            'PHP': '🐘',
            'Ruby': '💎',
            'Swift': '🦉',
            'Kotlin': '🎯',
            'C#': '🔷'
        };
        return icons[language] || '📄';
    };
    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };
    return (React.createElement("div", { className: "steampunk-panel p-6 h-full flex flex-col" },
        React.createElement("div", { className: "flex items-center gap-3 mb-6" },
            React.createElement("div", { className: "steampunk-gear" }),
            React.createElement("h3", { className: "text-xl font-bold text-white", style: { fontFamily: 'var(--heading-font)' } }, "Code Repository Vault"),
            React.createElement("div", { className: "steampunk-gear", style: { animationDirection: 'reverse' } })),
        !isConnected ? (
        /* Connection Form */
        React.createElement("div", { className: "steampunk-github" },
            React.createElement("div", { className: "text-center mb-6" },
                React.createElement("div", { className: "text-6xl mb-4" }, "\uD83D\uDD10"),
                React.createElement("h4", { className: "text-lg font-semibold text-antique-white mb-2" }, "Connect to GitHub Arsenal"),
                React.createElement("p", { className: "text-sm text-gray-300" }, "Link your mechanical repositories to the development forge")),
            !showConnectionForm ? (React.createElement("button", { onClick: () => setShowConnectionForm(true), className: "steampunk-button w-full" },
                React.createElement("span", { className: "mr-2" }, "\uD83D\uDD17"),
                "Establish Connection")) : (React.createElement("div", { className: "space-y-4" },
                React.createElement("div", null,
                    React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-2" }, "GitHub Personal Access Token"),
                    React.createElement("input", { type: "password", value: githubToken, onChange: (e) => setGithubToken(e.target.value), placeholder: "ghp_xxxxxxxxxxxxxxxxxxxx", className: "steampunk-input w-full" }),
                    React.createElement("p", { className: "text-xs text-gray-400 mt-1" }, "Create a token at GitHub \u2192 Settings \u2192 Developer settings \u2192 Personal access tokens")),
                React.createElement("div", { className: "flex gap-3" },
                    React.createElement("button", { onClick: handleConnect, disabled: !githubToken.trim() || isLoading, className: "steampunk-button flex-1" }, isLoading ? React.createElement("div", { className: "steampunk-loading w-4 h-4" }) : 'Connect'),
                    React.createElement("button", { onClick: () => {
                            setShowConnectionForm(false);
                            setGithubToken('');
                        }, className: "steampunk-button bg-gray-600 border-gray-600 hover:bg-gray-500" }, "Cancel")))))) : (
        /* Connected State */
        React.createElement("div", { className: "flex-1 flex flex-col" },
            React.createElement("div", { className: "steampunk-github mb-4" },
                React.createElement("div", { className: "flex items-center justify-between mb-4" },
                    React.createElement("div", { className: "flex items-center gap-2" },
                        React.createElement("span", { className: "text-emerald-accent text-lg" }, "\uD83D\uDD17"),
                        React.createElement("span", { className: "text-sm font-medium text-antique-white" }, "Connected to GitHub Arsenal")),
                    React.createElement("button", { onClick: onDisconnect, className: "text-rust-red hover:text-red-400 text-sm transition-colors" }, "Disconnect")),
                React.createElement("div", { className: "flex gap-3" },
                    React.createElement("button", { onClick: () => setShowCreateForm(true), className: "steampunk-button flex-1" },
                        React.createElement("span", { className: "mr-2" }, "\u2697\uFE0F"),
                        "Forge New Repository"),
                    selectedRepository && (React.createElement("button", { onClick: () => onSyncRepository(selectedRepository.id), className: "steampunk-button bg-emerald-accent border-emerald-accent hover:bg-green-600", disabled: isLoading },
                        React.createElement("span", { className: "mr-2" }, "\uD83D\uDD04"),
                        isLoading ? 'Syncing...' : 'Sync')))),
            showCreateForm && (React.createElement("div", { className: "steampunk-agent-card mb-4" },
                React.createElement("h4", { className: "text-lg font-semibold text-antique-white mb-4" }, "Forge New Repository"),
                React.createElement("div", { className: "space-y-4" },
                    React.createElement("div", null,
                        React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-1" }, "Repository Name"),
                        React.createElement("input", { type: "text", value: newRepoName, onChange: (e) => setNewRepoName(e.target.value), placeholder: "my-steampunk-project", className: "steampunk-input w-full" })),
                    React.createElement("div", null,
                        React.createElement("label", { className: "block text-sm font-medium text-antique-white mb-1" }, "Description"),
                        React.createElement("textarea", { value: newRepoDescription, onChange: (e) => setNewRepoDescription(e.target.value), placeholder: "A magnificent mechanical contraption...", className: "steampunk-input w-full h-20 resize-none" })),
                    React.createElement("div", { className: "flex items-center gap-2" },
                        React.createElement("input", { type: "checkbox", id: "private-repo", checked: newRepoPrivate, onChange: (e) => setNewRepoPrivate(e.target.checked), className: "rounded" }),
                        React.createElement("label", { htmlFor: "private-repo", className: "text-sm text-antique-white" }, "Private Repository (Secret blueprints)")),
                    React.createElement("div", { className: "flex gap-3" },
                        React.createElement("button", { onClick: handleCreateRepo, disabled: !newRepoName.trim() || isLoading, className: "steampunk-button flex-1" }, isLoading ? React.createElement("div", { className: "steampunk-loading w-4 h-4" }) : 'Create Repository'),
                        React.createElement("button", { onClick: () => setShowCreateForm(false), className: "steampunk-button bg-gray-600 border-gray-600 hover:bg-gray-500" }, "Cancel"))))),
            React.createElement("div", { className: "mb-4" },
                React.createElement("input", { type: "text", value: searchTerm, onChange: (e) => setSearchTerm(e.target.value), placeholder: "Search repositories...", className: "steampunk-input w-full" })),
            React.createElement("div", { className: "flex-1 overflow-y-auto steampunk-scroll space-y-3" }, filteredRepositories.length === 0 ? (React.createElement("div", { className: "text-center text-gray-400 mt-8" },
                React.createElement("div", { className: "text-4xl mb-4" }, "\uD83D\uDCC2"),
                React.createElement("p", null, "No repositories found in the archive"))) : (filteredRepositories.map((repo) => (React.createElement("div", { key: repo.id, className: `steampunk-repo-card cursor-pointer ${selectedRepository?.id === repo.id ? 'ring-2 ring-brass-primary' : ''}`, onClick: () => onSelectRepository(repo) },
                React.createElement("div", { className: "flex items-start justify-between mb-3" },
                    React.createElement("div", { className: "flex items-center gap-2" },
                        React.createElement("span", { className: "text-lg" }, getLanguageIcon(repo.language)),
                        React.createElement("div", null,
                            React.createElement("h4", { className: "font-semibold text-antique-white flex items-center gap-2" },
                                repo.name,
                                repo.private && React.createElement("span", { className: "text-xs bg-rust-red px-2 py-1 rounded" }, "\uD83D\uDD12 Private")),
                            repo.description && (React.createElement("p", { className: "text-sm text-gray-300 mt-1" }, repo.description))))),
                React.createElement("div", { className: "flex items-center justify-between text-xs text-gray-400" },
                    React.createElement("div", { className: "flex items-center gap-4" },
                        React.createElement("span", { className: "flex items-center gap-1" },
                            "\u2B50 ",
                            repo.stars),
                        React.createElement("span", { className: "flex items-center gap-1" },
                            "\uD83C\uDF74 ",
                            repo.forks),
                        React.createElement("span", null, repo.language)),
                    React.createElement("span", null,
                        "Updated ",
                        formatDate(repo.updatedAt))),
                React.createElement("div", { className: "flex gap-2 mt-3" },
                    React.createElement("button", { onClick: (e) => {
                            e.stopPropagation();
                            window.open(repo.url, '_blank');
                        }, className: "text-brass-primary hover:text-amber-glow transition-colors text-xs" }, "\uD83D\uDD17 View on GitHub"),
                    React.createElement("button", { onClick: (e) => {
                            e.stopPropagation();
                            onSyncRepository(repo.id);
                        }, className: "text-emerald-accent hover:text-green-400 transition-colors text-xs", disabled: isLoading }, "\uD83D\uDD04 Sync")))))))))));
};
export default SteampunkGitHubIntegration;
