"""Constants for the Life Time Fitness integration."""
import enum

DOMAIN = "lifetime_fitness"
VERSION = "0.0.0-dev"  # Updated by release workflow
ISSUE_URL = "https://github.com/GuyLewin/home-assistant-lifetime-fitness"
PLATFORM = "sensor"

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_START_OF_WEEK_DAY = "start_of_week_day"
CONF_START_OF_WEEK_DAY_VALUES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}
# Week starts on Monday by default
DEFAULT_START_OF_WEEK_DAY = 0

API_AUTH_ENDPOINT = "https://api.lifetimefitness.com/auth/v2/login"
API_AUTH_REQUEST_SUBSCRIPTION_KEY_HEADER = "ocp-apim-subscription-key"
# Value taken from any HTML page on my.lifetime.life
API_AUTH_REQUEST_SUBSCRIPTION_KEY_HEADER_VALUE = "924c03ce573d473793e184219a6a19bd"
API_AUTH_REQUEST_USERNAME_JSON_KEY = "username"
API_AUTH_REQUEST_PASSWORD_JSON_KEY = "password"
API_AUTH_TOKEN_JSON_KEY = "ssoId"
API_AUTH_MESSAGE_JSON_KEY = "message"
API_AUTH_STATUS_JSON_KEY = "status"

API_CLUB_VISITS_ENDPOINT_FORMATSTRING = \
    "https://myaccount.lifetimefitness.com/myaccount/api/member/clubvisits?end_date={end_date}&start_date={start_date}"
API_CLUB_VISITS_ENDPOINT_DATE_FORMAT = "%Y-%m-%d"
API_CLUB_VISITS_AUTH_HEADER = "X-LTF-SSOID"
API_CLUB_VISITS_TIMESTAMP_JSON_KEY = "usageDateTime"

VISITS_SENSOR_ID_SUFFIX = "_lifetime_visits"
VISITS_SENSOR_NAME_SUFFIX = " Life Time Visits"

UNIT_OF_MEASUREMENT = "times"

ATTR_VISITS_THIS_YEAR = "visits_this_year"
ATTR_VISITS_THIS_MONTH = "visits_this_month"
ATTR_VISITS_THIS_WEEK = "visits_this_week"
ATTR_LAST_VISIT_TIMESTAMP = "last_visit_timestamp"


class AuthenticationResults(enum.Enum):
    SUCCESS = 0
    PASSWORD_NEEDS_TO_BE_CHANGED = 1
    INVALID = 2
    TOO_MANY_ATTEMPTS = 3
    ACTIVATION_REQUIRED = 4
    DUPLICATE_EMAIL = 5


AUTHENTICATION_RESPONSE_MESSAGES = {
    AuthenticationResults.SUCCESS: "Success",
    AuthenticationResults.PASSWORD_NEEDS_TO_BE_CHANGED: "Password needs to be changed.",
    AuthenticationResults.INVALID: "Invalid username or password"
}
AUTHENTICATION_RESPONSE_STATUSES = {
    AuthenticationResults.INVALID: "-201",
    AuthenticationResults.TOO_MANY_ATTEMPTS: "-207",
    AuthenticationResults.ACTIVATION_REQUIRED: "-208",
    AuthenticationResults.DUPLICATE_EMAIL: "-209"
}
