#!/usr/bin/env python3
"""
Docker health check script for SDLC Orchestrator
"""
import sys
import requests
import time

# Constants
HTTP_OK = 200


def health_check():
    """Perform health check on the application"""
    try:
        # Check main application endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=10)

        if response.status_code == HTTP_OK:
            health_data = response.json()

            # Check if application is healthy
            if health_data.get('status') == 'healthy':
                logger.info("Health check PASSED: Application is healthy")
                return 0
            else:
                logger.info(f"Health check FAILED: Application status is {health_data.get('status')}")
                return 1
        else:
            logger.info(f"Health check FAILED: HTTP {response.status_code}")
            return 1

    except requests.exceptions.ConnectionError:
        logger.info("Health check FAILED: Could not connect to application")
        return 1
    except requests.exceptions.Timeout:
        logger.info("Health check FAILED: Request timed out")
        return 1
    except Exception as e:
        logger.info(f"Health check FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(health_check())
