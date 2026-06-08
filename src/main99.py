"""
Main entry point for the FastAPI application. This file starts the server and includes all the 
necessary routers for handling API requests. In the future, this file can also be used to set up middleware,
for the html. 
"""
from fastapi import FastAPI

from src.API_layer.routers import retrieval2
from src.API_layer.routers import auth
from fastapi.middleware.cors import CORSMiddleware

#app.add_middleware(
#    CORSMiddleware,
#    allow_origins=["*"],
#    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
#)

app = FastAPI(
    title="EU Compliance Assistant",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(retrieval2.router)


@app.get("/")
async def root():

    return {
        "application": "EU Compliance Assistant",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy"
    }