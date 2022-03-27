import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from graphql import app as GraphqlApp


app = FastAPI(docs_url=None, redoc_url=None,
              swagger_ui_parameters={"deepLinking": False})

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/graphql", GraphqlApp, name="graphql")
app.add_event_handler('startup', GraphqlApp.startup)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url if not (
            app.openapi_url is None) else "/openapi.json",
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url
         if not(app.swagger_ui_oauth2_redirect_url is None)
         else "", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url if not (
            app.openapi_url is None) else "/openapi.json",
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    tags: List[str] = []


@app.get("/items/", response_model=Item)
async def read_items():
    return [{"name": "Foo"}]


@app.get("/users/{username}")
async def read_user(username: str):
    return {"message": f"Hello {username}"}


if __name__ == "__main__":
    uvicorn.run("index:app", host="127.0.0.1",
                port=8000, reload=True, ws="websockets", log_level="info")
