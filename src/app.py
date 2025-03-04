from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, Request
import os
from src.service.request_handler import handle_request
from src.config.logging_config import setup_logging

setup_logging()

app = FastAPI(title="Huntflow Optimization API")

@app.post("/huntflow/webhook/applicant")
async def new_action(request: Request):
    return await handle_request(request)

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv("APP_PORT", "7707"))
    uvicorn.run(app, host="0.0.0.0", port=port)