import React, { useState, useEffect } from 'react';
import '../styles/steampunk.css';

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

interface GitHubIntegrationProps {
  repositories: Repository[];
  isConnected: boolean;
  onConnect: (token: string) => void;
  onDisconnect: () => void;
  onSelectRepository: (repo: Repository) => void;
  onCreateRepository: (name: string, description: string, isPrivate: boolean) => void;
  onSyncRepository: (repoId: string) => void;
  isLoading?: boolean;
  selectedRepository?: Repository;
}

export const SteampunkGitHubIntegration: React.FC<GitHubIntegrationProps> = ({
  repositories,
  isConnected,
  onConnect,
  onDisconnect,
  onSelectRepository,
  onCreateRepository,
  onSyncRepository,
  isLoading = false,
  selectedRepository
}) => {
  const [showConnectionForm, setShowConnectionForm] = useState(false);
  const [githubToken, setGithubToken] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newRepoName, setNewRepoName] = useState('');
  const [newRepoDescription, setNewRepoDescription] = useState('');
  const [newRepoPrivate, setNewRepoPrivate] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredRepositories = repositories.filter(repo =>
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    repo.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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

  const getLanguageIcon = (language: string) => {
    const icons: { [key: string]: string } = {
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="steampunk-panel p-6 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="steampunk-gear"></div>
        <h3 className="text-xl font-bold text-white" style={{ fontFamily: 'var(--heading-font)' }}>
          Code Repository Vault
        </h3>
        <div className="steampunk-gear" style={{ animationDirection: 'reverse' }}></div>
      </div>

      {!isConnected ? (
        /* Connection Form */
        <div className="steampunk-github">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🔐</div>
            <h4 className="text-lg font-semibold text-antique-white mb-2">
              Connect to GitHub Arsenal
            </h4>
            <p className="text-sm text-gray-300">
              Link your mechanical repositories to the development forge
            </p>
          </div>

          {!showConnectionForm ? (
            <button
              onClick={() => setShowConnectionForm(true)}
              className="steampunk-button w-full"
            >
              <span className="mr-2">🔗</span>
              Establish Connection
            </button>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-antique-white mb-2">
                  GitHub Personal Access Token
                </label>
                <input
                  type="password"
                  value={githubToken}
                  onChange={(e) => setGithubToken(e.target.value)}
                  placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                  className="steampunk-input w-full"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Create a token at GitHub → Settings → Developer settings → Personal access tokens
                </p>
              </div>
              
              <div className="flex gap-3">
                <button
                  onClick={handleConnect}
                  disabled={!githubToken.trim() || isLoading}
                  className="steampunk-button flex-1"
                >
                  {isLoading ? <div className="steampunk-loading w-4 h-4"></div> : 'Connect'}
                </button>
                <button
                  onClick={() => {
                    setShowConnectionForm(false);
                    setGithubToken('');
                  }}
                  className="steampunk-button bg-gray-600 border-gray-600 hover:bg-gray-500"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Connected State */
        <div className="flex-1 flex flex-col">
          {/* Connection Status & Actions */}
          <div className="steampunk-github mb-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-emerald-accent text-lg">🔗</span>
                <span className="text-sm font-medium text-antique-white">
                  Connected to GitHub Arsenal
                </span>
              </div>
              <button
                onClick={onDisconnect}
                className="text-rust-red hover:text-red-400 text-sm transition-colors"
              >
                Disconnect
              </button>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowCreateForm(true)}
                className="steampunk-button flex-1"
              >
                <span className="mr-2">⚗️</span>
                Forge New Repository
              </button>
              
              {selectedRepository && (
                <button
                  onClick={() => onSyncRepository(selectedRepository.id)}
                  className="steampunk-button bg-emerald-accent border-emerald-accent hover:bg-green-600"
                  disabled={isLoading}
                >
                  <span className="mr-2">🔄</span>
                  {isLoading ? 'Syncing...' : 'Sync'}
                </button>
              )}
            </div>
          </div>

          {/* Create Repository Form */}
          {showCreateForm && (
            <div className="steampunk-agent-card mb-4">
              <h4 className="text-lg font-semibold text-antique-white mb-4">
                Forge New Repository
              </h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-antique-white mb-1">
                    Repository Name
                  </label>
                  <input
                    type="text"
                    value={newRepoName}
                    onChange={(e) => setNewRepoName(e.target.value)}
                    placeholder="my-steampunk-project"
                    className="steampunk-input w-full"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-antique-white mb-1">
                    Description
                  </label>
                  <textarea
                    value={newRepoDescription}
                    onChange={(e) => setNewRepoDescription(e.target.value)}
                    placeholder="A magnificent mechanical contraption..."
                    className="steampunk-input w-full h-20 resize-none"
                  />
                </div>
                
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="private-repo"
                    checked={newRepoPrivate}
                    onChange={(e) => setNewRepoPrivate(e.target.checked)}
                    className="rounded"
                  />
                  <label htmlFor="private-repo" className="text-sm text-antique-white">
                    Private Repository (Secret blueprints)
                  </label>
                </div>
                
                <div className="flex gap-3">
                  <button
                    onClick={handleCreateRepo}
                    disabled={!newRepoName.trim() || isLoading}
                    className="steampunk-button flex-1"
                  >
                    {isLoading ? <div className="steampunk-loading w-4 h-4"></div> : 'Create Repository'}
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

          {/* Search */}
          <div className="mb-4">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search repositories..."
              className="steampunk-input w-full"
            />
          </div>

          {/* Repositories List */}
          <div className="flex-1 overflow-y-auto steampunk-scroll space-y-3">
            {filteredRepositories.length === 0 ? (
              <div className="text-center text-gray-400 mt-8">
                <div className="text-4xl mb-4">📂</div>
                <p>No repositories found in the archive</p>
              </div>
            ) : (
              filteredRepositories.map((repo) => (
                <div
                  key={repo.id}
                  className={`steampunk-repo-card cursor-pointer ${
                    selectedRepository?.id === repo.id ? 'ring-2 ring-brass-primary' : ''
                  }`}
                  onClick={() => onSelectRepository(repo)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getLanguageIcon(repo.language)}</span>
                      <div>
                        <h4 className="font-semibold text-antique-white flex items-center gap-2">
                          {repo.name}
                          {repo.private && <span className="text-xs bg-rust-red px-2 py-1 rounded">🔒 Private</span>}
                        </h4>
                        {repo.description && (
                          <p className="text-sm text-gray-300 mt-1">{repo.description}</p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <div className="flex items-center gap-4">
                      <span className="flex items-center gap-1">
                        ⭐ {repo.stars}
                      </span>
                      <span className="flex items-center gap-1">
                        🍴 {repo.forks}
                      </span>
                      <span>{repo.language}</span>
                    </div>
                    <span>Updated {formatDate(repo.updatedAt)}</span>
                  </div>
                  
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(repo.url, '_blank');
                      }}
                      className="text-brass-primary hover:text-amber-glow transition-colors text-xs"
                    >
                      🔗 View on GitHub
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSyncRepository(repo.id);
                      }}
                      className="text-emerald-accent hover:text-green-400 transition-colors text-xs"
                      disabled={isLoading}
                    >
                      🔄 Sync
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SteampunkGitHubIntegration;