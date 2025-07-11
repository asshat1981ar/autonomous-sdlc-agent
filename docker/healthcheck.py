#!/usr/bin/env python3
"""
Docker health check script for SDLC Orchestrator
"""
import sys
import requests
import time

def health_check():
    """Perform health check on the application"""
    try:
        # Check main application endpoint
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            
            # Check if application is healthy
            if health_data.get('status') == 'healthy':
                print("Health check PASSED: Application is healthy")
                return 0
            else:
                print(f"Health check FAILED: Application status is {health_data.get('status')}")
                return 1
        else:
            print(f"Health check FAILED: HTTP {response.status_code}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("Health check FAILED: Could not connect to application")
        return 1
    except requests.exceptions.Timeout:
        print("Health check FAILED: Request timed out")
        return 1
    except Exception as e:
        print(f"Health check FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(health_check())
