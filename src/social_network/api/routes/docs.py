import pathlib
import fastapi
from fastapi.openapi import docs
from starlette import requests, responses, staticfiles


def add_documentation_route(
    app: fastapi.FastAPI, static_files_path: pathlib.Path
) -> None:
    async def openapi_route(_: requests.Request) -> responses.JSONResponse:
        return responses.JSONResponse(app.openapi())

    async def custom_swagger_ui_html() -> responses.Response:
        return docs.get_swagger_ui_html(
            openapi_url="openapi.json",
            title="Social Network - Swagger UI",
            oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
            swagger_js_url="static/swagger-ui-bundle.js",
            swagger_css_url="static/swagger-ui.css",
        )

    async def redoc_html() -> responses.Response:
        return docs.get_redoc_html(
            openapi_url="openapi.json",
            title="Social Network - ReDoc",
            redoc_js_url="static/redoc.standalone.js",
        )

    app.add_route("/openapi.json", openapi_route, include_in_schema=False)
    app.mount(
        "/static", staticfiles.StaticFiles(directory=static_files_path), name="static"
    )
    app.add_api_route(
        path="/docs",
        endpoint=custom_swagger_ui_html,
        include_in_schema=False,
        methods=["GET"],
    )
    app.add_api_route(
        path="/redoc", endpoint=redoc_html, include_in_schema=False, methods=["GET"]
    )
