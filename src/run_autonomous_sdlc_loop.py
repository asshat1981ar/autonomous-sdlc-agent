import asyncio
import time
import sys
import os

# Adjust sys.path to include parent directory for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from refactored_orchestrator import EnhancedOrchestrator

enhanced_orchestrator = EnhancedOrchestrator()

async def autonomous_sdlc_loop(task: str, agents: list, iterations: int = 5, delay_seconds: int = 10):
    """
    Run an autonomous SDLC loop using the swarm paradigm.
    """
    for i in range(iterations):
        logger.info(f"Starting autonomous SDLC loop iteration {i+1}/{iterations}")
        result = await enhanced_orchestrator.collaborate(
            session_id=f"autonomous_sdlc_{int(time.time())}",
            paradigm='swarm',
            task=task,
            agents=agents,
            context={'mode': 'autonomous_sdlc'}
        )
        logger.info(f"Iteration {i+1} result status: {result.get('status', 'unknown')}")
        if i < iterations - 1:
            logger.info(f"Waiting {delay_seconds} seconds before next iteration...")
            await asyncio.sleep(delay_seconds)

if __name__ == "__main__":
    task = "Develop a microservice with REST API and database integration"
    agents = ['gemini', 'claude', 'openai']
    asyncio.run(autonomous_sdlc_loop(task, agents))
