import aiohttp
from fastapi import BackgroundTasks, FastAPI, Query, Body, Request
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from .config import Settings


app = FastAPI()
app.config = Settings()


class Metadata(BaseModel):
    display_phone_number: int
    phone_number_id: int


class ChangeValue(BaseModel):
    messaging_product: str
    metadata: Metadata
    contacts: List = []
    messages: List = []
    statuses: List = []


class Change(BaseModel):
    value: ChangeValue
    field: str


class EntryItem(BaseModel):
    id: str
    changes: List[Change]


class Model(BaseModel):
    object: str
    entry: List[EntryItem]


async def post_message_updates(model: Model, config: Settings):
    async with aiohttp.ClientSession() as http:
        for entry in model.entry:
            for change in entry.changes:
                endpoint_config = config.endpoints.get(
                    change.value.metadata.display_phone_number,
                    config.endpoints["default"],
                )
                endpoint = endpoint_config.endpoint.format(
                    metadata=change.value.metadata,
                )
                async with http.post(
                    endpoint,
                    json=change.value.dict(),
                    headers=endpoint_config.headers,
                ) as resp:
                    logger.debug(resp.status)


@app.get("/")
def get(challenge: int = Query(..., alias="hub.challenge")):
    return challenge


@app.post("/")
def process_webhook_updates(
    background_tasks: BackgroundTasks,
    request: Request,
    obj: Any = Body(...),
):
    try:
        obj: Model = Model.parse_obj(obj)
        background_tasks.add_task(post_message_updates, obj, request.app.config)
        return {"ok": True}
    except ValidationError as e:
        logger.bind(update=obj, error=e).error("Invalid request")
        raise e
