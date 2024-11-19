import asyncio

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.common.log_config import setup_logging
from loguru import logger

app = FastAPI(title="Duplication_widget")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/test_log")
def test_log():
    logger.info("Тестовый лог.")


@app.on_event("startup")
async def startup_event():
    setup_logging()
    logger.info("Виджет дубли сделок запущен.")
    loop = asyncio.get_event_loop()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
