import os


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_third_party_config() -> dict:
    """
    Phase 1: environment-variable configuration (local dev).
    Phase 2+: fetch from AWS Secrets Manager on EC2 via IAM role.
    """
    return {
        "RENTCAST_API_KEY": _required("RENTCAST_API_KEY"),
        "API_NINJAS_API_KEY": _required("API_NINJAS_API_KEY"),
        "GOOGLE_MAPS_API_KEY": _required("GOOGLE_MAPS_API_KEY"),
        "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "SMTP_PORT": int(os.getenv("SMTP_PORT", "465")),
        "SMTP_USERNAME": os.getenv("SMTP_USERNAME", ""),
        "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", ""),
    }

