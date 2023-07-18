from fastapi import FastAPI


def create_app():
    app = FastAPI()

    @app.get("/")
    def index():
        # TODO: maybe return some information about this service?
        return ""

    @app.get("/healthz")
    def health_check():
        return "ok"

    @app.get("/readyz")
    def readiness_check():
        return "ok"

    @app.on_event("startup")
    def on_startup():
        pass

    return app
