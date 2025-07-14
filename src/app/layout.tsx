"use client";

import React, { useState } from "react";
import SteampunkChatInterface from "../../components/SteampunkChatInterface";
import SteampunkFileUpload from "../../components/SteampunkFileUpload";
import SteampunkGitHubIntegration from "../../components/SteampunkGitHubIntegration";
import SteampunkAgentDevelopment from "../../components/SteampunkAgentDevelopment";
import AppInputForm from "../../components/AppInputForm";

import React, { useState } from "react";
import SteampunkChatInterface from "../../components/SteampunkChatInterface";
import SteampunkFileUpload from "../../components/SteampunkFileUpload";
import SteampunkGitHubIntegration from "../../components/SteampunkGitHubIntegration";
import SteampunkAgentDevelopment from "../../components/SteampunkAgentDevelopment";
import AppInputForm from "../../components/AppInputForm";
import OrchestratorDashboard from "../../components/OrchestratorDashboard";
import SystemPromptEditor from "../../components/SystemPromptEditor";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [activeTab, setActiveTab] = useState<
    | "chat"
    | "files"
    | "github"
    | "agents"
    | "inputform"
    | "dashboard"
    | "prompt"
  >("chat");

  const getTabIcon = (tab: string) => {
    const icons: { [key: string]: string } = {
      chat: "💬",
      files: "📁",
      github: "🔗",
      agents: "🤖",
      dashboard: "📊",
      prompt: "✍️",
    };
    return icons[tab] || "⚙️";
  };

  const getTabLabel = (tab: string) => {
    const labels: { [key: string]: string } = {
      chat: "Intelligence Console",
      files: "Blueprint Archive",
      github: "Repository Vault",
      agents: "Mind Foundry",
      dashboard: "Dashboard",
      prompt: "System Prompt",
    };
    return labels[tab] || tab;
  };

  return (
    <html lang="en">
      <head>
        <title>Autonomous SDLC Mechanica</title>
        <link
          href="https://fonts.googleapis.com/css2?family=Roboto+Mono&family=Roboto:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-coal-black text-antique-white font-roboto min-h-screen flex flex-col">
        {/* Header */}
        <header className="bg-gradient-to-r from-coal-black to-gray-800 border-b-2 border-brass-primary p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="steampunk-gear text-2xl"></div>
            <div>
              <h1
                className="text-2xl font-bold"
                style={{ fontFamily: "Roboto, monospace" }}
              >
                Autonomous SDLC Mechanica
              </h1>
              <p className="text-sm text-brass-primary">
                Industrial-Grade AI Development Console
              </p>
            </div>
          </div>
          {/* Placeholder for steam pressure and active agents */}
          <div className="flex items-center gap-6">
            <div className="text-amber-glow font-bold">75.0%</div>
            <div className="text-brass-primary font-bold">Active Agents: 2</div>
          </div>
        </header>

        {/* Navigation Tabs */}
        <nav className="bg-coal-black border-b border-brass-primary">
          <div className="flex">
            {(
              [
                "chat",
                "files",
                "github",
                "agents",
                "inputform",
                "dashboard",
                "prompt",
              ] as const
            ).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex items-center gap-2 px-6 py-4 border-r border-brass-primary transition-all ${
                  activeTab === tab
                    ? "bg-brass-gradient text-coal-black"
                    : "text-antique-white hover:bg-brass-primary hover:bg-opacity-20"
                }`}
                style={{ fontFamily: "Roboto, monospace" }}
              >
                <span className="text-lg">{getTabIcon(tab)}</span>
                {getTabLabel(tab)}
              </button>
            ))}
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 overflow-auto">
          {activeTab === "chat" && (
            <div className="h-full">
              <SteampunkChatInterface
                messages={[]}
                onSendMessage={(content, attachments) => {
                  console.log("Send message:", content, attachments);
                }}
              />
            </div>
          )}
          {activeTab === "files" && (
            <div className="p-6">
              <SteampunkFileUpload
                onFileUpload={(files) => {
                  // handle file upload logic here
                  console.log("Files uploaded:", files);
                }}
              />
            </div>
          )}
          {activeTab === "github" && (
            <div className="h-full">
              <SteampunkGitHubIntegration
                repositories={[]}
                isConnected={false}
                onConnect={(token) => {
                  console.log("GitHub connect:", token);
                }}
                onDisconnect={() => {
                  console.log("GitHub disconnect");
                }}
                onSelectRepository={(repo) => {
                  console.log("Select repo:", repo);
                }}
                onCreateRepository={(name, description, isPrivate) => {
                  console.log("Create repo:", { name, description, isPrivate });
                }}
                onSyncRepository={(repoId) => {
                  console.log("Sync repo:", repoId);
                }}
                isLoading={false}
                selectedRepository={undefined}
              />
            </div>
          )}
          {activeTab === "agents" && (
            <div className="h-full">
              <SteampunkAgentDevelopment
                agents={[]}
                availableModels={[]}
                onCreateAgent={(config) => {
                  console.log("Create agent:", config);
                }}
                onUpdateAgent={(id, config) => {
                  console.log("Update agent:", id, config);
                }}
                onDeleteAgent={(id) => {
                  console.log("Delete agent:", id);
                }}
                onTrainAgent={(id, trainingData) => {
                  console.log("Train agent:", id, trainingData);
                }}
                onTestAgent={(id, testPrompt) => {
                  console.log("Test agent:", id, testPrompt);
                }}
                isLoading={false}
              />
            </div>
          )}
          {activeTab === "inputform" && (
            <div className="h-full">
              <AppInputForm
                onSubmit={(idea) => {
                  console.log("Project idea submitted:", idea);
                }}
                isLoading={false}
                error={null}
              />
            </div>
          )}
          {activeTab === "dashboard" && (
            <div className="h-full">
              <OrchestratorDashboard />
            </div>
          )}
          {activeTab === "prompt" && (
            <div className="h-full">
              <SystemPromptEditor />
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="bg-coal-black border-t border-brass-primary p-4 text-sm text-gray-400 flex justify-between">
          <div>Powered by Steam & Silicon</div>
          <div>System Operational</div>
          <div>Memory Cores: 2/10</div>
          <div>Pressure: 75.0%</div>
          <div>Version: Mechanica v2.1.0</div>
        </footer>
      </body>
    </html>
  );
}
