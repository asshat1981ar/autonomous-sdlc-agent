"use client";

import React, { useState } from "react";

const defaultPrompt = "You are a helpful AI assistant specialized in software development tasks.";

export default function SystemPromptEditor() {
  const [prompt, setPrompt] = React.useState(() => {
    return localStorage.getItem("systemPrompt") || defaultPrompt;
  });
  const [error, setError] = React.useState("");

  const handleSave = () => {
    if (!prompt.trim()) {
      setError("System prompt cannot be empty.");
      return;
    }
    setError("");
    localStorage.setItem("systemPrompt", prompt);
    alert("System prompt saved.");
  };

  const handleReset = () => {
    setPrompt(defaultPrompt);
    setError("");
  };

  React.useEffect(() => {
    localStorage.setItem("systemPrompt", prompt);
  }, [prompt]);

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4 text-black">System Prompt Editor</h1>
      <p className="mb-4 text-gray-700">
        Edit the main system prompt used for AI calls. This prompt guides the AI's behavior.
      </p>
      <textarea
        className="w-full h-48 p-3 border border-gray-300 rounded font-mono text-black resize-none"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        aria-label="System prompt editor"
      />
      {error && <p className="text-red-600 mt-2">{error}</p>}
      <div className="mt-4 space-x-4">
        <button
          onClick={handleSave}
          className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800 transition"
        >
          Save
        </button>
        <button
          onClick={handleReset}
          className="bg-gray-200 text-black px-4 py-2 rounded hover:bg-gray-300 transition"
        >
          Reset
        </button>
      </div>
    </div>
  );
}
