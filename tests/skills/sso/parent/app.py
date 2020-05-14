# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from aiohttp import web
from aiohttp.web import Request, Response
from aiohttp.web_response import json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    ConversationState,
    MemoryStorage,
    UserState,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import BotFrameworkHttpClient
from botbuilder.schema import Activity
from botframework.connector.auth import SimpleCredentialProvider

from bots import ParentBot
from dialogs import MainDialog
from config import DefaultConfig
from adapter_with_error_handler import AdapterWithErrorHandler

CONFIG = DefaultConfig()

# Create MemoryStorage, UserState and ConversationState
MEMORY = MemoryStorage()
USER_STATE = UserState(MEMORY)
CONVERSATION_STATE = ConversationState(MEMORY)

# Create adapter.
# See https://aka.ms/about-bot-adapter to learn more about how bots work.
SETTINGS = BotFrameworkAdapterSettings(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
ADAPTER = AdapterWithErrorHandler(SETTINGS)

DIALOG = MainDialog(CONFIG)

CLIENT = BotFrameworkHttpClient(
    SimpleCredentialProvider(CONFIG.APP_ID, CONFIG.APP_PASSWORD)
)

# Create the Bot
BOT = ParentBot(CLIENT, CONFIG, DIALOG, CONVERSATION_STATE, USER_STATE)


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    # Main bot message handler.
    if "application/json" in req.headers["Content-Type"]:
        body = await req.json()
    else:
        return Response(status=415)

    activity = Activity().deserialize(body)
    auth_header = req.headers["Authorization"] if "Authorization" in req.headers else ""

    invoke_response = await ADAPTER.process_activity(
        activity, auth_header, BOT.on_turn
    )
    if invoke_response:
        return json_response(
            data=invoke_response.body, status=invoke_response.status
        )
    return Response(status=201)


APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/api/messages", messages)

if __name__ == "__main__":
    try:
        web.run_app(APP, host="localhost", port=CONFIG.PORT)
    except Exception as error:
        raise error
