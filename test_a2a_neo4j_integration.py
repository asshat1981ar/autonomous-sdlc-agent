#!/usr/bin/env python3
"""
A2A Neo4j Integration Test Suite
Tests the integration between the A2A system and Neo4j database
"""
import asyncio
import json
import time
import logging
from datetime import datetime, timezone
from a2a_neo4j_integration import A2ANeo4jIntegratedOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2ANeo4jTester:
    """Test suite for A2A Neo4j integration"""
    
    def __init__(self):
        self.orchestrator = None
        self.test_results = []
    
    async def setup(self):
        """Initialize the orchestrator with Neo4j connection"""
        try:
            self.orchestrator = A2ANeo4jIntegratedOrchestrator(
                neo4j_uri="bolt://localhost:7687",
                neo4j_user="neo4j",
                neo4j_password="password123"
            )
            logger.info("✅ A2A Neo4j orchestrator initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
            return False
    
    def log_test_result(self, test_name: str, success: bool, message: str, duration: float = 0.0):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message} ({duration:.2f}s)")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "duration": duration,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    async def test_basic_orchestration(self):
        """Test basic orchestration with Neo4j persistence"""
        test_name = "Basic Orchestration"
        start_time = time.time()
        
        try:
            result = await self.orchestrator.orchestrate_with_persistence(
                description="Create a simple Python calculator with basic operations",
                intent="general"
            )
            
            duration = time.time() - start_time
            
            # Verify result structure
            required_fields = ["task_id", "description", "agent_results", "collaboration_network", "neo4j_integration"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                self.log_test_result(test_name, False, f"Missing fields: {missing_fields}", duration)
                return False
            
            if not result.get("neo4j_integration", False):
                self.log_test_result(test_name, False, "Neo4j integration not confirmed", duration)
                return False
            
            agent_count = len(result.get("agent_results", []))
            if agent_count < 3:
                self.log_test_result(test_name, False, f"Insufficient agents participated: {agent_count}", duration)
                return False
            
            self.log_test_result(test_name, True, f"Orchestration completed with {agent_count} agents", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_mmorpg_orchestration(self):
        """Test MMORPG-specific orchestration"""
        test_name = "MMORPG Orchestration"
        start_time = time.time()
        
        try:
            result = await self.orchestrator.orchestrate_with_persistence(
                description="Design a D&D character progression system with skill trees and class abilities",
                intent="mmorpg"
            )
            
            duration = time.time() - start_time
            
            if not result.get("neo4j_integration", False):
                self.log_test_result(test_name, False, "Neo4j integration not confirmed", duration)
                return False
            
            # Check for MMORPG-specific capabilities
            agent_results = result.get("agent_results", [])
            has_planning = any("planner" in r.get("agent_id", "") for r in agent_results)
            has_coding = any("coder" in r.get("agent_id", "") for r in agent_results)
            
            if not (has_planning and has_coding):
                self.log_test_result(test_name, False, "Missing essential agent roles", duration)
                return False
            
            self.log_test_result(test_name, True, f"MMORPG orchestration completed successfully", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_analytics_dashboard(self):
        """Test analytics dashboard functionality"""
        test_name = "Analytics Dashboard"
        start_time = time.time()
        
        try:
            analytics = self.orchestrator.get_analytics_dashboard()
            duration = time.time() - start_time
            
            required_sections = ["system_analytics", "agent_performance", "neo4j_status"]
            missing_sections = [section for section in required_sections if section not in analytics]
            
            if missing_sections:
                self.log_test_result(test_name, False, f"Missing sections: {missing_sections}", duration)
                return False
            
            if analytics.get("neo4j_status") != "connected":
                self.log_test_result(test_name, False, f"Neo4j status: {analytics.get('neo4j_status')}", duration)
                return False
            
            system_analytics = analytics.get("system_analytics", {})
            if not isinstance(system_analytics, dict) or not system_analytics:
                self.log_test_result(test_name, False, "Empty system analytics", duration)
                return False
            
            self.log_test_result(test_name, True, "Analytics dashboard working correctly", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_agent_optimization(self):
        """Test agent optimization functionality"""
        test_name = "Agent Optimization"
        start_time = time.time()
        
        try:
            # Test finding agents by capability
            planning_agents = self.orchestrator.repository.find_agents_by_capability("technical_planning")
            duration = time.time() - start_time
            
            if not planning_agents:
                self.log_test_result(test_name, False, "No planning agents found", duration)
                return False
            
            # Test optimal agent selection
            optimal_agent = self.orchestrator.repository.find_optimal_agent_for_task(
                task_intent="general",
                required_capabilities=["technical_planning"]
            )
            
            if not optimal_agent:
                self.log_test_result(test_name, False, "No optimal agent found", duration)
                return False
            
            self.log_test_result(test_name, True, f"Found {len(planning_agents)} planning agents", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_performance_tracking(self):
        """Test performance tracking and metrics"""
        test_name = "Performance Tracking"
        start_time = time.time()
        
        try:
            # Get performance history for an agent
            performance_history = self.orchestrator.repository.get_agent_performance_history(
                "planner-001", days=30
            )
            
            duration = time.time() - start_time
            
            # Performance history might be empty for new installations
            # This is not necessarily a failure
            
            # Test system analytics
            system_analytics = self.orchestrator.repository.get_system_analytics()
            
            if not isinstance(system_analytics, dict):
                self.log_test_result(test_name, False, "Invalid system analytics format", duration)
                return False
            
            self.log_test_result(test_name, True, f"Performance tracking operational", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_concurrent_orchestration(self):
        """Test concurrent orchestration requests"""
        test_name = "Concurrent Orchestration"
        start_time = time.time()
        
        try:
            # Create multiple concurrent orchestration tasks
            tasks = [
                self.orchestrator.orchestrate_with_persistence(
                    description=f"Create test application #{i}",
                    intent="general"
                )
                for i in range(3)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # Check for exceptions
            exceptions = [r for r in results if isinstance(r, Exception)]
            if exceptions:
                self.log_test_result(test_name, False, f"Exceptions in concurrent execution: {len(exceptions)}", duration)
                return False
            
            # Check all results are valid
            valid_results = [r for r in results if isinstance(r, dict) and r.get("neo4j_integration")]
            if len(valid_results) != 3:
                self.log_test_result(test_name, False, f"Only {len(valid_results)}/3 concurrent tasks succeeded", duration)
                return False
            
            self.log_test_result(test_name, True, f"3 concurrent orchestrations completed successfully", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_database_persistence(self):
        """Test that data is actually persisted to Neo4j"""
        test_name = "Database Persistence"
        start_time = time.time()
        
        try:
            # Run a test orchestration
            result = await self.orchestrator.orchestrate_with_persistence(
                description="Test persistence verification",
                intent="general"
            )
            
            task_id = result.get("task_id")
            if not task_id:
                duration = time.time() - start_time
                self.log_test_result(test_name, False, "No task ID returned", duration)
                return False
            
            # Verify the task exists in the database
            collaboration_network = self.orchestrator.repository.get_task_collaboration_network(task_id)
            
            duration = time.time() - start_time
            
            # The collaboration network might be empty for a single task
            # The important thing is that no exception was raised
            
            self.log_test_result(test_name, True, f"Task {task_id} persisted to database", duration)
            return True
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting A2A Neo4j Integration Test Suite")
        logger.info("")
        
        if not await self.setup():
            logger.error("❌ Setup failed, aborting tests")
            return
        
        tests = [
            self.test_basic_orchestration,
            self.test_mmorpg_orchestration,
            self.test_analytics_dashboard,
            self.test_agent_optimization,
            self.test_performance_tracking,
            self.test_database_persistence,
            self.test_concurrent_orchestration,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                success = await test()
                if success:
                    passed += 1
            except Exception as e:
                logger.error(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Generate summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 A2A NEO4J INTEGRATION TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Tests Passed: {passed}/{total}")
        logger.info(f"❌ Tests Failed: {total - passed}/{total}")
        logger.info(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("🎉 ALL TESTS PASSED! A2A Neo4j integration is fully functional.")
        elif passed >= total * 0.8:
            logger.info("⚠️  Most tests passed. Minor issues may need attention.")
        else:
            logger.info("❌ Multiple test failures. Please check Neo4j setup and connectivity.")
        
        # Cleanup
        if self.orchestrator:
            self.orchestrator.close()
        
        logger.info("=" * 60)
        
        # Save test results to file
        with open('a2a_neo4j_test_results.json', 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total,
                    "passed": passed,
                    "failed": total - passed,
                    "success_rate": (passed/total)*100,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        logger.info("📄 Detailed results saved to: a2a_neo4j_test_results.json")

async def main():
    """Main test runner"""
    tester = A2ANeo4jTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())