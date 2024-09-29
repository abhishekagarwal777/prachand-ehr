from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app instance
app = FastAPI()

# Function to initialize the app and log a warning
def initialize():
    print("Security is disabled. Configure 'security.auth-type' to disable this warning.")

# Call initialize function
initialize()

# Configure CORS if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No security configuration; all endpoints are open.
@app.get("/")
async def root():
    return {"message": "Security is disabled. All endpoints are open."}
