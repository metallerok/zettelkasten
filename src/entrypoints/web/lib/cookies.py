from src import app_globals


def make_fingerprint_cookie() -> str:
    return f"{app_globals.app_name}._fingerprint"


def make_refresh_token_cookie() -> str:
    return f"{app_globals.app_name}.session.refresh_token"
