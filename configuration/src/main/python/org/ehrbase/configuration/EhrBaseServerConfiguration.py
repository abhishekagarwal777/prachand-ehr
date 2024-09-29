from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from some_module import (
    ServiceModuleConfiguration,
    RestModuleConfiguration,
    RestEHRScapeModuleConfiguration,
    AqlEngineModuleConfiguration
)

app = FastAPI()

# Initialize configurations or modules
@app.on_event("startup")
async def startup_event():
    # Initialize modules
    ServiceModuleConfiguration().startup()
    RestModuleConfiguration().startup()
    RestEHRScapeModuleConfiguration().startup()
    AqlEngineModuleConfiguration().startup()

# Example route
@app.get("/")
async def read_root():
    return {"message": "Hello World"}

# Periodic task example (if needed)
@app.on_event("startup")
@repeat_every(seconds=60)  # Adjust the interval as needed
async def periodic_task():
    # Perform a periodic task
    pass
