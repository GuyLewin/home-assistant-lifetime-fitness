"""API client for Life Time Fitness"""
from aiohttp import ClientError
from datetime import date

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
    API_CLUB_VISITS_ENDPOINT,
    API_CLUB_VISITS_ENDPOINT_DATE_FORMAT,
    API_CLUB_VISITS_AUTH_HEADER,
)


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

        async with self._clientsession.get(
            API_CLUB_VISITS_ENDPOINT_FORMATSTRING.format(
                start_date=start_date.strftime(API_CLUB_VISITS_ENDPOINT_DATE_FORMAT),
                end_date=end_date.strftime(API_CLUB_VISITS_ENDPOINT_DATE_FORMAT),
            ),
            headers={API_CLUB_VISITS_AUTH_HEADER: self._sso_token},
        ) as response:
            if response.status == 401:
                raise ApiAuthExpired
            response_json = await response.json()
            return response_json

    async def _get_visits(self):
        if self._sso_token is None:
            raise ApiAuthRequired

        async with self._clientsession.get(
            API_CLUB_VISITS_ENDPOINT,
            headers={API_CLUB_VISITS_AUTH_HEADER: self._sso_token},
        ) as response:
            if response.status == 401:
                raise ApiAuthExpired
            response_json = await response.json()
            return response_json

    async def update(self):
        try:
            try:
                self.result_json = await self._get_visits()
            except ApiAuthExpired:
                self.authenticate()
                # Try again after authenticating
                self.result_json = await self._get_visits()
        except Exception as e:
            self.update_successful = False
            raise e


class ApiCannotConnect(Exception):
    """Client can't connect to API server"""


class ApiInvalidAuth(Exception):
    """API server returned invalid auth"""


class ApiAuthRequired(Exception):
    """This API call requires authenticating beforehand"""


class ApiAuthExpired(Exception):
    """Authentication has expired"""
