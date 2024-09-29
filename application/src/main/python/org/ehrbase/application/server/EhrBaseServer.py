from fastapi import FastAPI
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Define configuration parameters here
    pass

class EhrBaseServer:
    def __init__(self):
        self.settings = Settings()  # Load configuration from environment or a file
        self.app = FastAPI()

    def run(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="info")

    def setup_routes(self):
        @self.app.get("/")
        def read_root():
            return {"message": "Welcome to EHRbase Server"}

# Entry point for the server application
if __name__ == "__main__":
    server = EhrBaseServer()
    server.setup_routes()
    server.run()
