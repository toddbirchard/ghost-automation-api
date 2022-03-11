"""FastAPI configuration."""
import datetime
from os import getenv, path

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings, EmailStr

# Load variables from .env
BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))


class Settings(BaseSettings):
    app_name: str = "JAMStack API"
    title: str = "JAMStack API"
    description: str = "API to automate optimizations for JAMStack sites."
    items_per_user: int = 50
    debug: bool = True

    # General Config
    SECRET_KEY: str = getenv("SECRET_KEY")
    ENVIRONMENT: str = getenv("ENVIRONMENT")
    dt: datetime.datetime = datetime.datetime.today()
    CORS_ORIGINS: list = [
        "http://hackersandslackers.com",
        "https://hackersandslackers.app",
        "http://localhost",
        "http://localhost:8080",
        "http://api.hackersandslackers.com",
        "https://api.hackersandslackers.com",
        "http://zapier.com",
        "https://zapier.com",
        "https://zapier.com/",
        "https://zapier.com/*",
        "*",
    ]
    API_TAGS = (
        [
            {
                "name": "posts",
                "description": "Sanitation and optimization of post metadata.",
            },
            {
                "name": "accounts",
                "description": "User account signup and actions.",
            },
            {
                "name": "authors",
                "description": "Author management.",
            },
            {
                "name": "newsletter",
                "description": "Ghost newsletter subscriptions.",
            },
            {
                "name": "analytics",
                "description": "Migrate site traffic & search query analytics.",
            },
            {
                "name": "images",
                "description": "Image optimization for retina and mobile devices.",
            },
            {
                "name": "github",
                "description": "Github notifications for new issues/PRs.",
            },
        ],
    )

    class Config:
        env_file = ".env"

    # Database
    SQLALCHEMY_DATABASE_URI: str = getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_DATABASE_PEM: str = getenv("SQLALCHEMY_DATABASE_PEM")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "ssl": {"key": SQLALCHEMY_DATABASE_PEM},
        "check_same_thread": False
    }

    # Algolia API
    ALGOLIA_SEARCHES_ENDPOINT: str = "https://analytics.algolia.com/2/searches"
    ALGOLIA_APP_ID: str = getenv("ALGOLIA_APP_ID")
    ALGOLIA_API_KEY: str = getenv("ALGOLIA_API_KEY")

    # GCP
    GCP_PROJECT: str = getenv("GCP_PROJECT")
    GCP_PROJECT_ID: str = getenv("GCP_PROJECT_ID")

    # Google BigQuery
    GCP_BIGQUERY_TABLE: str = getenv("GCP_BIGQUERY_TABLE")
    GCP_BIGQUERY_DATASET: str = getenv("GCP_BIGQUERY_DATASET")
    GCP_BIGQUERY_URI: str = f"bigquery://{GCP_PROJECT}/{GCP_BIGQUERY_DATASET}"

    # Plausible
    PLAUSIBLE_BREAKDOWN_ENDPOINT = "https://plausible.io/api/v1/stats/breakdown"
    PLAUSIBLE_API_TOKEN: str = getenv("PLAUSIBLE_API_TOKEN")

    # Google Cloud storage
    GCP_BUCKET_URL: str = getenv("GCP_BUCKET_URL")
    GCP_BUCKET_NAME: str = getenv("GCP_BUCKET_NAME")
    GCP_BUCKET_FOLDER: list = [f'{dt.year}/{dt.strftime("%m")}']
    GCP_LYNX_DIRECTORY: str = "roundup"
    # GOOGLE_APPLICATION_CREDENTIALS: str = getenv("GOOGLE_APPLICATION_CREDENTIALS")
    # GCP_CREDENTIALS = service_account.Credentials.from_service_account_file(
    #     f"{basedir}/{GOOGLE_APPLICATION_CREDENTIALS}"
    # )

    # Ghost
    GHOST_BASE_URL: str = getenv("GHOST_BASE_URL")
    GHOST_ADMIN_API_URL: str = f"{GHOST_BASE_URL}/ghost/api/v3/admin"
    GHOST_CONTENT_API_URL: str = f"{GHOST_BASE_URL}/ghost/api/v3/"
    GHOST_CONTENT_API_KEY: str = getenv("GHOST_CONTENT_API_KEY")
    GHOST_API_USERNAME: str = getenv("GHOST_API_USERNAME")
    GHOST_API_PASSWORD: str = getenv("GHOST_API_PASSWORD")
    GHOST_CLIENT_ID: str = getenv("GHOST_CLIENT_ID")
    GHOST_ADMIN_API_KEY: str = getenv("GHOST_ADMIN_API_KEY")
    GHOST_API_EXPORT_URL: str = f"{GHOST_BASE_URL}/admin/db/"
    GHOST_NETLIFY_BUILD_HOOK: str = getenv("GHOST_NETLIFY_BUILD_HOOK")

    GHOST_AUTHOR_TODD_ID: str = "1"
    GHOST_AUTHOR_MATT_ID: str = "61304d7e74047afda1c21620"

    # Mailgun
    MAILGUN_EMAIL_SERVER: str = getenv("MAILGUN_EMAIL_SERVER")
    MAILGUN_NEWSLETTER_TEMPLATE: str = getenv("MAILGUN_NEWSLETTER_TEMPLATE")
    MAILGUN_SENDER_API_KEY: str = getenv("MAILGUN_SENDER_API_KEY")
    MAILGUN_FROM_SENDER: EmailStr = getenv("MAILGUN_FROM_SENDER")
    MAILGUN_PERSONAL_EMAIL: str = getenv("MAILGUN_PERSONAL_EMAIL")
    MAILGUN_PASSWORD: str = getenv("MAILGUN_PASSWORD")
    MAILGUN_SUBJECT_LINE: str = "To Hack or to Slack; That is the Question."

    MAILGUN_CONF = ConnectionConfig(
        MAIL_USERNAME="api",
        MAIL_PASSWORD=MAILGUN_PASSWORD,
        MAIL_FROM=MAILGUN_FROM_SENDER,
        MAIL_FROM_NAME="Todd Birchard",
        MAIL_PORT=587,
        MAIL_SERVER=MAILGUN_EMAIL_SERVER,
        MAIL_TLS=True,
        MAIL_SSL=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    # Mixpanel
    MIXPANEL_API_TOKEN: str = getenv("MIXPANEL_API_TOKEN")

    # Twilio
    TWILIO_SENDER_PHONE: str = getenv("TWILIO_SENDER_PHONE")
    TWILIO_RECIPIENT_PHONE: str = getenv("TWILIO_RECIPIENT_PHONE")
    TWILIO_AUTH_TOKEN: str = getenv("TWILIO_AUTH_TOKEN")
    TWILIO_ACCOUNT_SID: str = getenv("TWILIO_ACCOUNT_SID")

    # Datadog
    DATADOG_API_KEY: str = getenv("DATADOG_API_KEY")
    DATADOG_APP_KEY: str = getenv("DATADOG_APP_KEY")
    dd_trace: bool = getenv("DATADOG_TRACE_ENABLED")

    # Github
    GH_USERNAME: str = getenv("GH_USERNAME")
    GH_API_KEY: str = getenv("GH_API_KEY")


settings = Settings()
