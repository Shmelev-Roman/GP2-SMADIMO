import requests
import json
import structlog
from typing import List

from api_parser.data import config
from api_parser.utils import logging
from api_parser.models import BuildingModel, PriceListItem


class CianApiParser:
    def __init__(self) -> None:
        self.logger: structlog.typing.FilteringBoundLogger = logging.setup_logger().bind(type="cian_parser")
        self.session = requests.Session()

        if config.ACCESS_TOKEN is None:
            raise ValueError("Access token is not defined!")

        self.session.headers = {
            'Authorization': f'Bearer {config.ACCESS_TOKEN}'
        }

    def get_new_buildings(self) -> List[BuildingModel]:
        response = json.loads(
            self.session.get(
                url=config.CIAN_API_URL + 'v2/get-newbuildings/'
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
                url=config.CIAN_API_URL + 'v2/get-prices/'
            ).content
        )

        if 'errors' in response:
            raise ValueError(response['message'])

        if 'priceList' not in response.keys():
            raise ValueError("Error while getting list of prices!")

        return [PriceListItem(**prices) for prices in response['priceList']]


if __name__ == '__main__':
    cianParser = CianApiParser()

