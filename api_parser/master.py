import os
import requests
import json
import structlog
from datetime import datetime, timedelta
from typing import List
import time

from api_parser.data import config
from api_parser.uitls import logging
from api_parser.models import BuildingModel, PriceListItem


class CianApiParser:
    def __init__(self) -> None:
        self.logger: structlog.typing.FilteringBoundLogger = logging.setup_logger().bind(type="cian_parser")

        self.session = requests.Session()

        if config.CIAN_ONE_TIME_TOKEN:
            self._login()
        else:
            # Load tokens from file if they exist
            self._load_tokens_from_file()

    def _load_tokens_from_file(self) -> None:
        file_path = config.BASE_DIR.parent / 'bearer_token.json'

        if os.path.exists(file_path):
            with open(file_path, 'r') as token_file:
                tokens = json.load(token_file)
                config.ACCESS_TOKEN = tokens.get('ACCESS_TOKEN')
                config.REFRESH_TOKEN = tokens.get('REFRESH_TOKEN')
                self.logger.info('Tokens loaded from file.')

    def _save_tokens_to_file(self) -> None:
        tokens = {
            'ACCESS_TOKEN': config.ACCESS_TOKEN,
            'REFRESH_TOKEN': config.REFRESH_TOKEN
        }
        with open(config.BASE_DIR.parent / 'bearer_token.json', 'w') as token_file:
            json.dump(tokens, token_file)
        self.logger.info('Tokens saved to file.')

    def _login(self) -> None:
        response = json.loads(
            self.session.post(
                url=config.CIAN_API_URL + 'v1/login/',
                data=json.dumps(
                    {
                        "token": config.CIAN_ONE_TIME_TOKEN
                    }
                )
            ).content
        )

        if 'errors' in response:
            raise ValueError(response['message'])

        config.ACCESS_TOKEN = response['accessToken']
        config.REFRESH_TOKEN = response['refreshToken']

        self._save_tokens_to_file()
        self.logger.info('Successfully authenticated by one-time-token!')

    def _refresh_access_token(self) -> None:
        if config.REFRESH_TOKEN is None:
            raise ValueError("Refresh token is not defined!")

        response = json.loads(
            self.session.post(
                url=config.CIAN_API_URL + 'v1/refresh-token/',
                data=json.dumps(
                    {
                        'refreshToken': config.REFRESH_TOKEN
                    }
                )
            ).content
        )

        if 'errors' in response:
            raise ValueError(response['message'])

        config.ACCESS_TOKEN = response['accessToken']
        config.REFRESH_TOKEN = response['refreshToken']

        self._save_tokens_to_file()
        self.logger.info('Bearer token updated successfully!')

    def get_new_buildings(self) -> List[BuildingModel]:
        if config.ACCESS_TOKEN is None:
            raise ValueError("Access token is not defined!")

        response = json.loads(
            self.session.get(
                url=config.CIAN_API_URL + 'v2/get-newbuildings/',
                headers={
                    'Authorization': f'Bearer {config.ACCESS_TOKEN}'
                }
            ).content
        )

        if 'errors' in response:
            raise ValueError(response['message'])

        if 'newbuildingList' not in response.keys():
            raise ValueError("Error while getting list of building!")

        return [BuildingModel(**building) for building in response['newbuildingList']]

    def get_prices(self) -> list:
        if config.ACCESS_TOKEN is None:
            raise ValueError("Access token is not defined!")

        response = json.loads(
            self.session.get(
                url=config.CIAN_API_URL + 'v2/get-prices/',
                headers={
                    'Authorization': f'Bearer {config.ACCESS_TOKEN}'
                }
            ).content
        )

        if 'errors' in response:
            raise ValueError(response['message'])

        if 'priceList' not in response.keys():
            raise ValueError("Error while getting list of prices!")

        return [PriceListItem(**prices) for prices in response['priceList']]


if __name__ == '__main__':
    cianParser = CianApiParser()
