import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://brainjam:brainjam@localhost:5432/brainjam",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Realtime
    WS_JWT_AUDIENCE = os.environ.get("WS_JWT_AUDIENCE", "brainjam")
