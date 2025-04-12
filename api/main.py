# FastAPI app entrypoint
from fastapi import FastAPI
from api.workload import router as workload_router

app = FastAPI()
app.include_router(workload_router)
