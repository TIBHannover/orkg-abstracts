import logging
import requests
import urllib.parse
import time

from typing import Tuple, Union

from src.services._base import BaseMetadataService


def respect_rate_limits(func):
    def wrapper(self, *args, **kwargs):
        time.sleep(3)
        return func(self, *args, **kwargs)

    return wrapper


class SemanticscholarService(BaseMetadataService):
    """
    The SemanticscholarService fetches politely abstract information from semanticscholar API by respecting the
    request rates of 100 requests / 5 min which is equivalent to sending one request every 3 seconds.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__(self.logger)

        self.source_name = 'semanticscholar'

    @respect_rate_limits
    def _by_doi(self, doi: str) -> Union[Tuple[str, str], None]:
        if not doi:
            return None

        url_encoded_doi = urllib.parse.quote_plus(doi)
        url = 'https://api.semanticscholar.org/v1/paper/{}'.format(url_encoded_doi)

        response = requests.get(url)
        if not response.ok:
            self.logger.warning('Request error returns response: {}'.format(response.__dict__))
            return None

        response = response.json()

        if 'abstract' in response and response['abstract']:
            return self.source_name, response['abstract']

        return None

    @respect_rate_limits
    def _by_title(self, title: str) -> Union[Tuple[str, str], None]:
        if not title:
            return None

        url_encoded_title = urllib.parse.quote_plus(title)
        url = 'https://api.semanticscholar.org/graph/v1/paper/search?query={}&fields=abstract,title'.format(
            url_encoded_title)

        response = requests.get(url)
        if not response.ok:
            self.logger.warning('Request error returns response: {}'.format(response.__dict__))
            return None

        response = response.json()

        if 'data' in response:
            for paper in response['data']:
                if title.lower() == paper['title'].lower() and paper['abstract']:
                    return self.source_name, paper['abstract']

        return None

