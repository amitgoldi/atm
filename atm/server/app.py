import motor
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_health import health
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from atm.server.models.atm import AtmContent
from atm.server.routes.atm import atm_router
from atm.server.services.refill import RefillService
from atm.server.settings import MongoDbSettings


def build_app():
    app = FastAPI()
    app.include_router(atm_router, tags=["ATM"], prefix="/atm")
    app.add_api_route("/health", health([]))
    return app


app = build_app()


@app.on_event("startup")
async def on_startup():
    await init()


async def init(mongo_client=None):
    await init_db(mongo_client)
    await RefillService.prefill()


async def init_db(mongo_client):
    mongodb = MongoDbSettings()

    client = mongo_client or motor.motor_asyncio.AsyncIOMotorClient(mongodb.uri)

    await init_beanie(database=client.get_database(name=mongodb.database),
                      document_models=[AtmContent])


@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def read_root():
    html_content = """
        <html>
            <head>
                <title>ATM Service</title>
            </head>
            <body>
                <h1>Welcome to ATM Service!</h1>
                <p><a href="/docs">API Docs</a></p>
            </body>
        </html>
    """
    return html_content
