from time import time
from dotenv import load_dotenv
from sqlalchemy.engine import Engine as DatabaseEngine
from sqlalchemy import Connection as DatabaseConnection
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa
from fastapi import FastAPI, APIRouter, status, Request
import uvicorn

# Config
from src.Shared.Config.AppConfig import AppConfig

# Shared
from src.Shared.DependencyInjection.Container import Container
from src.Shared.Logging.Interfaces import ILogger
from src.Shared.Logging.Models import Logger
from src.Shared.Events.Models import EventDispatcher

# Authentication
from src.Authentication.Infrastructure.Dependencies import AuthenticationDependencies
from src.Authentication.Infrastructure.Http.Routes import Routes as AuthenticationRoutes
from src.Authentication.Infrastructure.Http.Controller import AuthenticationController

# Session
from src.Session.Infrastructure.Dependencies import SessionDependencies
from src.Session.Infrastructure.Http.Routes import Routes as SessionRoutes
from src.Session.Infrastructure.Http.Controller import SessionController

# Load environment variables from .env file
load_dotenv()

# Initialize the app configuration
appConfig: AppConfig = AppConfig.FromEnv()

# Initialize the Container
container: Container = Container.FromAppConfig(appConfig)

# Singletons registration
container.RegisterSingletons(
    {
        AppConfig.__name__: lambda container: appConfig,
        DatabaseEngine.__name__: lambda container: sa.create_engine(
            appConfig.databaseUrl,
        ),
        ILogger.__name__: lambda container: Logger(target=appConfig.logTarget),
        EventDispatcher.__name__: lambda container: EventDispatcher(),
    }
)

# Factories registration
container.RegisterFactories(
    {
        DatabaseConnection.__name__: lambda container: container.Get(
            DatabaseEngine.__name__
        ).connect(),
        DatabaseSession.__name__: lambda container: sessionmaker(
            bind=container.Get(DatabaseEngine.__name__)
        )(),
    }
)

# Context dependencies
AuthenticationDependencies.RegisterDependencies(container)
SessionDependencies.RegisterDependencies(container)

# Initialize FastAPI app
app: FastAPI = FastAPI(title=appConfig.appName, version=appConfig.version)

# Setup routers for API versions
apiV1Router: APIRouter = APIRouter(prefix="/api/v1")

# Setup Routes
AuthenticationRoutes.RegisterRoutes(
    router=apiV1Router, controller=container.Get(AuthenticationController.__name__)
)
SessionRoutes.RegisterRoutes(
    router=apiV1Router, controller=container.Get(SessionController.__name__)
)


# Index
@apiV1Router.get("/", tags=["Index"], status_code=status.HTTP_200_OK)
async def Index():
    return {"message": "Welcome to the Authentication API", "version": appConfig.version}


# Health Check
@apiV1Router.get("/health", tags=["Health"], status_code=status.HTTP_200_OK)
async def HealthCheck():
    return {"status": "healthy"}


# Catch-all for undefined routes
@apiV1Router.get("/{fullPath:path}", tags=["CatchAll"], status_code=status.HTTP_404_NOT_FOUND)
async def CatchAll(fullPath: str):
    return {"error": "Endpoint not found", "path": fullPath}


# Include the router in the main app
app.include_router(apiV1Router)


# Register middleware, event handlers, etc.
@app.middleware("http")
async def LogIncomingRequests(request: Request, call_next):  # pylint: disable=invalid-name
    logger: ILogger = container.Get(ILogger.__name__)
    logger.Info("=" * 50)
    logger.Info(f"{appConfig.appName} API")
    logger.Info("Incoming request...")
    logger.Info(f"[{request.method}] {request.url}")
    logger.Info(f"Headers: {dict(request.headers)}")
    logger.Info("+" * 50)

    response = await call_next(request)

    logger.Info(f"Response headers: {dict(response.headers)}")
    logger.Info(f"Response status: {response.status_code}")
    logger.Info("=" * 50)
    return response


@app.middleware("http")
async def CalculateProcessingTime(request: Request, call_next):  # pylint: disable=invalid-name
    logger: ILogger = container.Get(ILogger.__name__)
    startTime = time()
    response = await call_next(request)
    processTime = time() - startTime
    response.headers["X-Process-Time"] = str(processTime)
    logger.Info(f"Processed request in {processTime:.4f} seconds")
    return response


# Run
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=appConfig.host,
        port=appConfig.port,
        log_level="info" if appConfig.debug else "warning",
        reload=appConfig.debug,
    )
