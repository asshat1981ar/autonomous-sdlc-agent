import { agentPersonas } from "./agent_personas";
import { OpenRouterAIProvider } from "./ai_providers";
import { AgentOrchestrator } from "./agent_orchestrator";

async function autonomousDevelopmentLoop() {
  const orchestrator = new AgentOrchestrator();

  // Define a default system prompt for AI providers
  const defaultSystemPrompt = "You are a helpful AI assistant specialized in software development tasks.";

  // Initialize AI providers for MCP servers with OpenRouterAIProvider
  const aiProviders = {
    github: new OpenRouterAIProvider({ apiKey: process.env.BLACKBOX_API_KEY || "", systemPrompt: defaultSystemPrompt }),
    playwright: new OpenRouterAIProvider({ apiKey: process.env.BLACKBOX_API_KEY || "", systemPrompt: defaultSystemPrompt }),
    memory: new OpenRouterAIProvider({ apiKey: process.env.BLACKBOX_API_KEY || "", systemPrompt: defaultSystemPrompt }),
    think: new OpenRouterAIProvider({ apiKey: process.env.BLACKBOX_API_KEY || "", systemPrompt: defaultSystemPrompt }),
    blender: new OpenRouterAIProvider({ apiKey: process.env.BLACKBOX_API_KEY || "", systemPrompt: defaultSystemPrompt }),
    activepieces: new OpenRouterAIProvider({ apiKey: process.env.BLACKBOX_API_KEY || "", systemPrompt: defaultSystemPrompt }),
  };

  // Create sessions for each persona with aiProviders
  orchestrator.createSession("session-code-analyst", "Code Analyst", agentPersonas, aiProviders);
  orchestrator.createSession("session-tester", "Tester", agentPersonas, aiProviders);
  orchestrator.createSession("session-documenter", "Documenter", agentPersonas, aiProviders);
  orchestrator.createSession("session-reasoner", "Reasoner", agentPersonas, aiProviders);
  orchestrator.createSession("session-3d-modeler", "3D Modeler", agentPersonas, aiProviders);

  // Define tasks for each persona
  const codeAnalystTasks = [
    "Analyze code quality",
    "Suggest refactoring",
    "Perform static analysis",
  ];

  const testerTasks = [
    "Run UI tests",
    "Run integration tests",
    "Report test results",
  ];

  const documenterTasks = [
    "Generate API documentation",
    "Update user guides",
    "Maintain changelog",
  ];

  const reasonerTasks = [
    "Record thoughts on current progress",
    "Plan next development steps",
    "Coordinate agent collaboration",
  ];

  const modelerTasks = [
    "Create 3D models for new features",
    "Modify existing scenes",
    "Export assets for integration",
  ];

  // Run tasks sequentially for each persona
  await orchestrator.runSequentialTasks("session-code-analyst", codeAnalystTasks);
  await orchestrator.runSequentialTasks("session-tester", testerTasks);
  await orchestrator.runSequentialTasks("session-documenter", documenterTasks);
  await orchestrator.runSequentialTasks("session-reasoner", reasonerTasks);
  await orchestrator.runSequentialTasks("session-3d-modeler", modelerTasks);

  // Retrieve and log session histories
  console.log("Code Analyst History:", orchestrator.getSessionHistory("session-code-analyst"));
  console.log("Tester History:", orchestrator.getSessionHistory("session-tester"));
  console.log("Documenter History:", orchestrator.getSessionHistory("session-documenter"));
  console.log("Reasoner History:", orchestrator.getSessionHistory("session-reasoner"));
  console.log("3D Modeler History:", orchestrator.getSessionHistory("session-3d-modeler"));
}

autonomousDevelopmentLoop().catch(console.error);
