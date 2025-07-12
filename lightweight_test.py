#!/usr/bin/env python3
"""
Lightweight test runner to verify fixes
"""

import asyncio
import sys
import os
import time

def test_imports():
    """Test that critical imports work"""
    logger.info("🔍 Testing imports...")

    try:
        from src.services.bridges.github_codex_bridge import github_codex_bridge
        logger.info("   ✅ GitHub Codex bridge import successful")
    except Exception as e:
        logger.info(f"   ❌ GitHub Codex bridge import failed: {e}")
        return False

    try:
        from src.services.bridges.mcp_bridge import mcp_bridge
        logger.info("   ✅ MCP bridge import successful")
    except Exception as e:
        logger.info(f"   ❌ MCP bridge import failed: {e}")
        return False

    try:
        from src.services.bridges.bridge_manager import bridge_manager
        logger.info("   ✅ Bridge manager import successful")
    except Exception as e:
        logger.info(f"   ❌ Bridge manager import failed: {e}")
        return False

    return True

async def test_basic_functionality():
    """Test basic functionality"""
    logger.info("\n⚙️  Testing basic functionality...")

    try:
        # Test GitHub bridge
        from src.services.bridges.github_codex_bridge import github_codex_bridge
        health = await github_codex_bridge.health_check()
        if health.get('status') == 'healthy':
            logger.info("   ✅ GitHub bridge health check passed")
        else:
            logger.info("   ❌ GitHub bridge health check failed")
            return False

        # Test code generation
        result = await github_codex_bridge.generate_code("create a function", "python")
        if result.get('success'):
            logger.info("   ✅ GitHub bridge code generation passed")
        else:
            logger.info("   ❌ GitHub bridge code generation failed")
            return False

    except Exception as e:
        logger.info(f"   ❌ GitHub bridge test failed: {e}")
        return False

    try:
        # Test MCP bridge
        from src.services.bridges.mcp_bridge import mcp_bridge
        health = await mcp_bridge.health_check()
        if health.get('status') in ['healthy', 'degraded']:
            logger.info("   ✅ MCP bridge health check passed")
        else:
            logger.info("   ❌ MCP bridge health check failed")
            return False

    except Exception as e:
        logger.info(f"   ❌ MCP bridge test failed: {e}")
        return False

    return True

async def test_orchestrator():
    """Test orchestrator functionality"""
    logger.info("\n🎼 Testing orchestrator...")

    try:
        from refactored_orchestrator import enhanced_orchestrator

        result = await enhanced_orchestrator.collaborate(
            session_id="lightweight_test",
            paradigm="mesh",
            task="Test lightweight functionality",
            agents=['claude', 'gemini'],
            context={'test_mode': True}
        )

        if result.get('status') == 'completed':
            logger.info("   ✅ Orchestrator collaboration test passed")
            return True
        else:
            logger.info("   ❌ Orchestrator collaboration test failed")
            return False

    except Exception as e:
        logger.info(f"   ❌ Orchestrator test failed: {e}")
        return False

def test_file_structure():
    """Test that key files exist"""
    logger.info("\n📁 Testing file structure...")

    critical_files = [
        'src/services/bridges/mcp_bridge.py',
        'src/services/bridges/bridge_manager.py',
        'src/services/bridges/github_codex_bridge.py',
        'components/SteampunkApp.tsx',
        'styles/steampunk.css'
    ]

    missing_files = []
    for file_path in critical_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        logger.info(f"   ❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        logger.info(f"   ✅ All {len(critical_files)} critical files present")
        return True

async def main():
    """Main lightweight test runner"""
    logger.info("🧪 LIGHTWEIGHT TEST SUITE")
    logger.info("=" * 40)

    start_time = time.time()
    tests_passed = 0
    total_tests = 4

    # Run tests
    if test_file_structure():
        tests_passed += 1

    if test_imports():
        tests_passed += 1

    if await test_basic_functionality():
        tests_passed += 1

    if await test_orchestrator():
        tests_passed += 1

    # Summary
    duration = time.time() - start_time
    success_rate = (tests_passed / total_tests) * 100

    logger.info(f"\n📊 LIGHTWEIGHT TEST SUMMARY")
    logger.info("=" * 30)
    logger.info(f"   Tests Passed: {tests_passed}/{total_tests}")
    logger.info(f"   Success Rate: {success_rate:.1f}%")
    logger.info(f"   Duration: {duration:.2f}s")

    if tests_passed == total_tests:
        logger.info(f"\n✅ ALL LIGHTWEIGHT TESTS PASSED!")
        logger.info(f"🎉 System is ready for full testing")
        return 0
    else:
        logger.info(f"\n❌ SOME TESTS FAILED")
        logger.info(f"🔧 Additional fixes may be needed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)