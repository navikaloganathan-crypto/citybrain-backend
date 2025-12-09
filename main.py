from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from services.routing.router import router as routing_router
from services.recommendations.router import router as recommendations_router
from services.tours.router import router as tours_router

app = FastAPI()

# Routers
app.include_router(routing_router)
app.include_router(recommendations_router)
app.include_router(tours_router)

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return {"status": "Backend is running!"}

