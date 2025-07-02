from app.core.config import settings
from zoneinfo import ZoneInfo

BASE_URL = 'http://127.0.0.1:8000'
PROFILE_IMG_ROUTE_PREFIX = '/profile/img'
tzinfo = ZoneInfo(settings.tz)
