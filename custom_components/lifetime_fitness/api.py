"""API client for Life Time Fitness"""
from aiohttp import ClientError, ClientResponseError
from datetime import date
from http import HTTPStatus
import logging

from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    API_AUTH_ENDPOINT,
    API_AUTH_REQUEST_USERNAME_JSON_KEY,
    API_AUTH_REQUEST_PASSWORD_JSON_KEY,
    API_AUTH_REQUEST_SUBSCRIPTION_KEY_HEADER,
    API_AUTH_REQUEST_SUBSCRIPTION_KEY_HEADER_VALUE,
    API_AUTH_STATUS_JSON_KEY,
    API_AUTH_STATUS_OK,
    API_AUTH_TOKEN_JSON_KEY,
    API_CLUB_VISITS_ENDPOINT_FORMATSTRING,
    API_CLUB_VISITS_ENDPOINT_DATE_FORMAT,
    API_CLUB_VISITS_AUTH_HEADER,
)

_LOGGER = logging.getLogger(__name__)


class Api:
    def __init__(self, hass, username: str, password: str) -> None:
        self._username = username
        self._password = password
        self._clientsession = async_create_clientsession(hass)
        self._sso_token = None

        self.update_successful = True
        self.result_json = None

    def get_username(self):
        return self._username

    async def authenticate(self):
        try:
            async with self._clientsession.post(
                API_AUTH_ENDPOINT,
                json={
                    API_AUTH_REQUEST_USERNAME_JSON_KEY: self._username,
                    API_AUTH_REQUEST_PASSWORD_JSON_KEY: self._password,
                },
                headers={
                    API_AUTH_REQUEST_SUBSCRIPTION_KEY_HEADER: API_AUTH_REQUEST_SUBSCRIPTION_KEY_HEADER_VALUE
                },
            ) as response:
                response_json = await response.json()
                if response_json[API_AUTH_STATUS_JSON_KEY] != API_AUTH_STATUS_OK:
                    raise ApiInvalidAuth
                self._sso_token = response_json[API_AUTH_TOKEN_JSON_KEY]
        except ClientError:
            raise ApiCannotConnect

    async def _get_visits_between_dates(self, start_date: date, end_date: date):
        if self._sso_token is None:
            raise ApiAuthRequired

        try:
            async with self._clientsession.get(
                API_CLUB_VISITS_ENDPOINT_FORMATSTRING.format(
                    start_date=start_date.strftime(API_CLUB_VISITS_ENDPOINT_DATE_FORMAT),
                    end_date=end_date.strftime(API_CLUB_VISITS_ENDPOINT_DATE_FORMAT),
                ),
                headers={API_CLUB_VISITS_AUTH_HEADER: self._sso_token},
            ) as response:
                response_json = await response.json()
                return response_json
        except ClientResponseError as err:
            if err.status == HTTPStatus.UNAUTHORIZED:
                raise ApiAuthExpired
            raise err

    async def update(self):
        today = date.today()
        first_day_of_the_year = date(today.year, 1, 1)
        try:
            try:
                self.result_json = await self._get_visits_between_dates(first_day_of_the_year, today)
            except ApiAuthExpired:
                await self.authenticate()
                # Try again after authenticating
                self.result_json = await self._get_visits_between_dates(first_day_of_the_year, today)
        except Exception as e:
            self.update_successful = False
            _LOGGER.exception("Unexpected exception during Life Time API update")
            raise e


class ApiCannotConnect(Exception):
    """Client can't connect to API server"""


class ApiInvalidAuth(Exception):
    """API server returned invalid auth"""


class ApiAuthRequired(Exception):
    """This API call requires authenticating beforehand"""


class ApiAuthExpired(Exception):
    """Authentication has expired"""
