import os
import argparse
from agent_registry import AgentRegistry
from metrics import MetricsServer

def main():
    """Main with enhanced functionality."""
    # Determine mode
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["api","cli"], default=os.getenv("AI_MODE","api"))
    args = parser.parse_args()

    # Start metrics
    metrics = MetricsServer(port=8001)
    metrics.start()

    # Load registry and agents
    registry = AgentRegistry()
    registry.load_from_config("config.yaml")

    if args.mode == "api":
        from server import create_api_app
        app = create_api_app(registry, metrics)
        app.run(host="0.0.0.0", port=5000)
    else:
        from cli import run_cli_loop
        run_cli_loop(registry, metrics)

if __name__ == "__main__":
    main()
