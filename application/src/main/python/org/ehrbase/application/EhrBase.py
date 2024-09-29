import argparse
import sys
from ehrbase_server import EhrBaseServer
from ehrbase_cli import EhrBaseCli

def main():
    parser = argparse.ArgumentParser(description="EHRbase Application")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode"
    )
    args = parser.parse_args()

    if args.cli:
        cli = EhrBaseCli()
        cli.run()
    else:
        server = EhrBaseServer()
        server.setup_routes()
        server.run()

if __name__ == "__main__":
    main()


from fastapi import FastAPI

class EhrBaseCli:
    def __init__(self):
        self.app = FastAPI()

    def run(self):
        print("Running CLI...")
        # Implement your CLI logic here

# Entry point for CLI
if __name__ == "__main__":
    cli = EhrBaseCli()
    cli.run()


from fastapi import FastAPI
import uvicorn

class EhrBaseServer:
    def __init__(self):
        self.app = FastAPI()

    def setup_routes(self):
        @self.app.get("/")
        def read_root():
            return {"message": "Welcome to EHRbase Server"}

    def run(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="info")

# Entry point for server
if __name__ == "__main__":
    server = EhrBaseServer()
    server.setup_routes()
    server.run()
