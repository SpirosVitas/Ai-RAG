from fastapi import FastAPI

from src.API_layer.routers import retrieval2

app = FastAPI(
    title="EU Compliance Assistant",
    version="1.0.0",
)

app.include_router(retrieval2.router)


@app.get("/")
async def root():

    return {
        "status": "healthy"
    }