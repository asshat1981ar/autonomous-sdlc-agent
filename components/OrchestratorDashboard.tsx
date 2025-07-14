"use client";

import React, { useState, useEffect } from "react";

interface Task {
  id: string;
  description: string;
  assignedAgent: string;
  status: "pending" | "in-progress" | "completed" | "failed";
  retryCount: number;
  lastError?: string;
}

const sampleTasks: Task[] = [
  {
    id: "task-1",
    description: "Analyze code quality",
    assignedAgent: "Code Analyst",
    status: "in-progress",
    retryCount: 1,
  },
  {
    id: "task-2",
    description: "Run UI tests",
    assignedAgent: "Tester",
    status: "failed",
    retryCount: 3,
    lastError: "Timeout error",
  },
  {
    id: "task-3",
    description: "Generate API documentation",
    assignedAgent: "Documenter",
    status: "pending",
    retryCount: 0,
  },
];

export default function OrchestratorDashboard() {
  const [tasks, setTasks] = useState<Task[]>(sampleTasks);

  // Placeholder for fetching real task data
  useEffect(() => {
    // Fetch tasks from API or state management
  }, []);

  const retryTask = (taskId: string) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === taskId
          ? { ...task, status: "in-progress", retryCount: task.retryCount + 1, lastError: undefined }
          : task
      )
    );
  };

  const rerouteTask = (taskId: string) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === taskId
          ? { ...task, status: "pending", lastError: undefined }
          : task
      )
    );
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-black">Orchestrator Dashboard</h1>
      <table className="min-w-full border border-gray-300">
        <thead className="bg-gray-100">
          <tr>
            <th className="border border-gray-300 px-4 py-2 text-left">Task ID</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Description</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Assigned Agent</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Status</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Retry Count</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Last Error</th>
            <th className="border border-gray-300 px-4 py-2 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id} className="hover:bg-gray-50">
              <td className="border border-gray-300 px-4 py-2">{task.id}</td>
              <td className="border border-gray-300 px-4 py-2">{task.description}</td>
              <td className="border border-gray-300 px-4 py-2">{task.assignedAgent}</td>
              <td className="border border-gray-300 px-4 py-2 capitalize">{task.status}</td>
              <td className="border border-gray-300 px-4 py-2">{task.retryCount}</td>
              <td className="border border-gray-300 px-4 py-2 text-red-600">{task.lastError || "-"}</td>
              <td className="border border-gray-300 px-4 py-2 space-x-2">
                <button
                  onClick={() => retryTask(task.id)}
                  className="bg-black text-white px-3 py-1 rounded hover:bg-gray-800 transition"
                >
                  Retry
                </button>
                <button
                  onClick={() => rerouteTask(task.id)}
                  className="bg-gray-200 text-black px-3 py-1 rounded hover:bg-gray-300 transition"
                >
                  Reroute
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
