import logging
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, ORJSONResponse
from redis.exceptions import RedisError

from .admin.utils import register_admin_view
from .api import router
from .config import Config, get_config
from .exceptions import HTTPException
from .logging import get_logging_config
from .middleware import add_middlewares
from .rq.utils import (
    shutdown_redis_resources,
    startup_redis_resources,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    config = get_config()
    startup_redis_resources(config)
    yield
    shutdown_redis_resources()


def patch_openapi_schema(app: FastAPI) -> None:
    openapi_schema = app.openapi()
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if (
                isinstance(method, dict)
                and "responses" in method
                and "422" in method["responses"]
            ):
                method["responses"].pop("422")
    app.openapi_schema = openapi_schema


def redis_exception_handler(request: Request, exc: RedisError) -> ORJSONResponse:
    logger.error(
        "Redis error encountered for request %s: %s (%s)",
        request.url.path,
        exc,
        type(exc).__name__,
    )
    return ORJSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": (
                "The service is temporarily unavailable due to an issue with a backend service. "
                "Please try again later"
            ),
        },
    )


def validation_exception_handler(_: Request, exc: RequestValidationError) -> ORJSONResponse:
    errors: dict[str, str] = {str(error["loc"][-1]): error["msg"] for error in exc.errors()}
    return ORJSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid input data",
            "errors": errors,
        },
    )


def http_exception_handler(_: Request, exc: HTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


def register_not_found_exception_handler(app: FastAPI, config: Config) -> None:
    @app.exception_handler(404)
    async def not_found_exception_handler(_: Request, __: Exception) -> FileResponse:
        return FileResponse(
            f"{config.static_dir}/404.html",
            status_code=status.HTTP_404_NOT_FOUND,
        )


def register_static_routes(app: FastAPI, config: Config) -> None:
    app.mount(
        "/assets",
        StaticFiles(directory=config.assets_dir),
        name="assets",
    )
    @app.get("/", response_class=FileResponse, include_in_schema=False)
    async def serve_index():
        return FileResponse(f"{config.static_dir}/index.html")


def init_app():
    config = get_config()
    dictConfig(get_logging_config(config.debug))
    app = FastAPI(debug=config.debug, lifespan=lifespan)
    add_middlewares(app, config)
    register_admin_view(app, config)
    app.include_router(router)
    app.add_exception_handler(RedisError, redis_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    register_static_routes(app, config)
    register_not_found_exception_handler(app, config)
    patch_openapi_schema(app)
    return app
