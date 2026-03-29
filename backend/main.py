from fastapi import FastAPI
import time

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/state")
def state():
    return {
        "timestamp": str(int(time.time())),
        "merkle_root": "0x" + "0" * 64,  # Placeholder for actual merkle root
        "status": "ACTIVE"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
