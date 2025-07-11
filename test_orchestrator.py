#!/usr/bin/env python3
"""
Test script to demonstrate SDLC Orchestrator functionality
"""
import asyncio
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.ai_providers_simple import orchestrator

async def test_orchestrator():
    """Test the SDLC orchestrator with different collaboration paradigms"""
    
    print("SDLC Orchestrator Test Suite")
    print("=" * 50)
    
    # Test Task: Create a simple web API
    test_task = "Create a REST API for a todo list application with CRUD operations"
    test_agents = ['gemini', 'claude', 'openai']
    
    paradigms = [
        'orchestra',
        'mesh', 
        'swarm',
        'weaver',
        'ecosystem'
    ]
    
    for paradigm in paradigms:
        print(f"\nTesting {paradigm.upper()} Paradigm")
        print("-" * 40)
        
        try:
            session_id = f"test_{paradigm}"
            result = await orchestrator.collaborate(
                session_id=session_id,
                paradigm=paradigm, 
                task=test_task,
                agents=test_agents
            )
            
            print(f"Success: {result['paradigm']}")
            print(f"Task: {result['task']}")
            print(f"Agents: {', '.join(result['agents'])}")
            
            if 'conductor_guidance' in result:
                print(f"Conductor: {result['conductor_guidance'][:100]}...")
            if 'conversations' in result:
                print(f"Conversations: {len(result['conversations'])} exchanges")
            if 'emergent_patterns' in result:
                print(f"Emergent Patterns: Available")
            if 'context_analysis' in result:
                print(f"Context Analysis: Available")
            if 'emergent_synthesis' in result:
                print(f"Ecosystem Evolution: Available")
                
        except Exception as e:
            print(f"Error in {paradigm}: {e}")
    
    print(f"\nTesting Bridge Services")
    print("-" * 40)
    
    # Test bridge initialization
    bridge_result = await orchestrator.initialize_bridges()
    if bridge_result['success']:
        print("Bridge services initialized successfully")
        
        # Test enhanced code generation
        code_result = await orchestrator.generate_code_with_bridges(
            "Create a Python function to validate email addresses",
            language="python",
            paradigm="orchestra"
        )
        print(f"Enhanced Code Generation: {code_result.get('success', False)}")
        
    else:
        print(f"Bridge services: {bridge_result.get('error', 'Not available')}")
    
    print(f"\nOrchestrator Status")
    print("-" * 40)
    print(f"Active Sessions: {len(orchestrator.active_sessions)}")
    print(f"Available Providers: {list(orchestrator.providers.keys())}")
    print(f"Bridge Enhanced: {orchestrator.bridge_initialized}")

if __name__ == "__main__":
    print("Starting SDLC Orchestrator Test...")
    asyncio.run(test_orchestrator())
    print("\nTest Complete!")
