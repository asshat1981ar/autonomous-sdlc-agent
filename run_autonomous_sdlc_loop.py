#!/usr/bin/env python3
import asyncio
import time
from refactored_orchestrator import enter_autonomous_sdlc_mode

async def autonomous_sdlc_loop(task: str, agents: list, iterations: int = 5, delay_seconds: int = 10):
    """
    Run the autonomous SDLC mode in a loop for a given number of iterations with delay.
    """
    for i in range(iterations):
        logger.info(f"Starting autonomous SDLC iteration {i+1}/{iterations}")
        try:
            result = await enter_autonomous_sdlc_mode(task, agents)
            logger.info(f"Iteration {i+1} result status: {result.get('status', 'unknown')}")
        except Exception as e:
            logger.info(f"Iteration {i+1} encountered an error: {e}")
        if i < iterations - 1:
            logger.info(f"Waiting {delay_seconds} seconds before next iteration...")
            await asyncio.sleep(delay_seconds)
    logger.info("Completed all autonomous SDLC loop iterations.")

if __name__ == "__main__":
    task_description = "Develop a microservice with REST API and database integration"
    agent_list = ['gemini', 'claude', 'openai']
    asyncio.run(autonomous_sdlc_loop(task_description, agent_list))
