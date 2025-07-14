"use client";

import React, { useState } from "react";
import OrchestratorDashboard from "../../components/OrchestratorDashboard";
import SystemPromptEditor from "../../components/SystemPromptEditor";

export default function HomePage() {
  const [view, setView] = useState<"dashboard" | "prompt">("dashboard");

  return (
    <div className="min-h-screen bg-white text-black font-sans">
      <header className="flex items-center justify-between p-4 border-b border-gray-300">
        <h1 className="text-2xl font-bold">Multi-Agent Orchestration Platform</h1>
        <nav>
          <button
            onClick={() => setView("dashboard")}
            className={`mr-4 px-3 py-1 rounded ${
              view === "dashboard" ? "bg-black text-white" : "bg-gray-200 text-black"
            } hover:bg-gray-800 hover:text-white transition`}
          >
            Dashboard
          </button>
          <button
            onClick={() => setView("prompt")}
            className={`px-3 py-1 rounded ${
              view === "prompt" ? "bg-black text-white" : "bg-gray-200 text-black"
            } hover:bg-gray-800 hover:text-white transition`}
          >
            System Prompt
          </button>
        </nav>
      </header>
      <main className="p-6 max-w-7xl mx-auto">
        {view === "dashboard" && <OrchestratorDashboard />}
        {view === "prompt" && <SystemPromptEditor />}
      </main>
    </div>
  );
}
