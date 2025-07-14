
interface AgentSession {
  persona: any;
  context: any;
  history: string[];
  aiProvider: any;
}

interface AgentSession {
  persona: any;
  context: any;
  history: string[];
  aiProvider: any;
}

interface RetryPolicy {
  maxRetries: number;
  intervalSec: number;
}

export class AgentOrchestrator {
  private sessions: Map<string, AgentSession> = new Map();
  private retryPolicy: RetryPolicy = { maxRetries: 3, intervalSec: 10 };

  createSession(sessionId: string, personaName: string, agentPersonas: any, aiProviders: any): void {
    const persona = agentPersonas.find((p: any) => p.name === personaName);
    if (!persona) {
      throw new Error(`Persona ${personaName} not found`);
    }
    // Assign AI provider based on persona role or name
    let aiProviderKey = "memory"; // default
    if (personaName === "Code Analyst") aiProviderKey = "github";
    else if (personaName === "Tester") aiProviderKey = "playwright";
    else if (personaName === "Reasoner") aiProviderKey = "think";
    else if (personaName === "3D Modeler") aiProviderKey = "blender";
    else if (personaName === "Documenter") aiProviderKey = "activepieces";

    this.sessions.set(sessionId, {
      persona,
      context: {},
      history: [],
      aiProvider: aiProviders[aiProviderKey],
    });
  }

  async runSequentialTasks(sessionId: string, tasks: string[]): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    for (const task of tasks) {
      console.log(`[${session.persona.name}] Processing task: ${task}`);
      session.history.push(task);

      let attempt = 0;
      let success = false;

      while (attempt <= this.retryPolicy.maxRetries && !success) {
        try {
          const response = await session.aiProvider.generate_response(task);
          console.log(`[${session.persona.name}] Response: ${response.response}`);
          session.history.push(response.response);
          success = true;
        } catch (error) {
          attempt++;
          console.error(`[${session.persona.name}] Error processing task (attempt ${attempt}):`, error);
          if (attempt <= this.retryPolicy.maxRetries) {
            console.log(`[${session.persona.name}] Retrying in ${this.retryPolicy.intervalSec} seconds...`);
            await new Promise((resolve) => setTimeout(resolve, this.retryPolicy.intervalSec * 1000));
          } else {
            console.error(`[${session.persona.name}] Max retries reached for task: ${task}`);
            // Fallback strategy could be implemented here
          }
        }
      }
    }
  }

  getSessionHistory(sessionId: string): string[] {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }
    return session.history;
  }
}
