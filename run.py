# One-line purpose: start the app (python3 run.py). Host 0.0.0.0 so the preview or a judge can reach it.
import os

import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.app.api.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), reload=False)
