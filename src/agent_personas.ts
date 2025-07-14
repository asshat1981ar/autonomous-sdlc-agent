export interface AgentPersona {
  name: string;
  role: string;
  description: string;
  capabilities: string[];
}

export const agentPersonas: AgentPersona[] = [
  {
    name: "Code Analyst",
    role: "Analyze and improve code quality",
    description: "Focuses on code quality, refactoring, and static analysis using GitHub MCP and Memory MCP.",
    capabilities: ["code analysis", "refactoring", "static analysis", "memory management"],
  },
  {
    name: "Tester",
    role: "Perform UI and integration testing",
    description: "Uses Playwright MCP for UI and integration testing automation.",
    capabilities: ["UI testing", "integration testing", "automation"],
  },
  {
    name: "Documenter",
    role: "Generate and maintain documentation",
    description: "Creates and updates documentation using Activepieces and Memory MCP.",
    capabilities: ["documentation generation", "workflow automation", "memory management"],
  },
  {
    name: "Reasoner",
    role: "Record thoughts, plan, and guide collaboration",
    description: "Uses Think MCP to record thoughts, plan tasks, and coordinate agent collaboration.",
    capabilities: ["reasoning", "planning", "collaboration"],
  },
  {
    name: "3D Modeler",
    role: "Perform 3D modeling tasks",
    description: "Uses Blender MCP for 3D modeling and scene manipulation tasks.",
    capabilities: ["3D modeling", "scene manipulation"],
  },
];
