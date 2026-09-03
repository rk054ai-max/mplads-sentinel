from fastapi import FastAPI

app = FastAPI(title="MPLADS Sentinel")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "mplads-sentinel"}
