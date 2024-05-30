from typing import Any, Awaitable, Callable, MutableMapping

import uvicorn

Scope = MutableMapping[str, Any]
Message = MutableMapping[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


async def handle_lifespan(scope: Scope, receive: Receive, send: Send) -> None:
    """Handle lifespan scope"""
    assert scope["type"] == "lifespan"

    while True:
        message = await receive()

        # Startup - receive event
        # https://asgi.readthedocs.io/en/latest/specs/lifespan.html#startup-receive-event
        # Sent to the application when the server is ready to startup
        # and receive connections, but before it has started to do so.
        if message["type"] == "lifespan.startup":
            # Startup Complete - send event
            # https://asgi.readthedocs.io/en/latest/specs/lifespan.html#startup-complete-send-event
            # Sent by the application when it has completed its startup.
            # A server must wait for this message
            # before it starts processing connections.
            await send({"type": "lifespan.startup.complete"})

        # Shutdown - receive event
        # https://asgi.readthedocs.io/en/latest/specs/lifespan.html#shutdown-receive-event
        # Sent to the application when the server has stopped accepting connections
        # and closed all active connections.
        elif message["type"] == "lifespan.shutdown":
            # Shutdown Complete - send event
            # https://asgi.readthedocs.io/en/latest/specs/lifespan.html#shutdown-complete-send-event
            # Sent by the application when it has completed its cleanup.
            # A server must wait for this message before terminating.
            await send({"type": "lifespan.shutdown.complete"})
            break


async def handle_http(scope: Scope, receive: Receive, send: Send) -> None:
    """Handle HTTP scope"""
    assert scope["type"] == "http"

    while True:
        message = await receive()

        # Disconnect - receive event
        # https://asgi.readthedocs.io/en/latest/specs/www.html#disconnect-receive-event
        # Sent to the application if receive is called after a response has been sent
        # or after the HTTP connection has been closed.
        if message["type"] == "http.disconnect":
            return

        if not message["more_body"]:
            break

    # Response Start - send event
    # https://asgi.readthedocs.io/en/latest/specs/www.html#response-start-send-event
    # Sent by the application to start sending a response to the client.
    # Needs to be followed by at least one response content message.
    response_message = {
        "type": "http.response.start",
        "status": 200,
    }
    await send(response_message)

    # Response Body - send even
    # https://asgi.readthedocs.io/en/latest/specs/www.html#response-body-send-event
    # Continues sending a response to the client.
    response_message = {
        "type": "http.response.body",
        "body": message["body"],
        "more_body": False,
    }
    await send(response_message)


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    if scope["type"] == "lifespan":
        await handle_lifespan(scope, receive, send)
    elif scope["type"] == "http":
        await handle_http(scope, receive, send)


def main() -> None:
    uvicorn.run(app)


if __name__ == "__main__":
    main()
