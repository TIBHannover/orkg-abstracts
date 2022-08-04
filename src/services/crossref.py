import logging
import requests
import urllib.parse
from typing import Tuple, Union

from src.services._base import BaseMetadataService


class CrossrefService(BaseMetadataService):
    """
    The CrossrefService fetches abstract information from Crossref API.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__(self.logger)

        self.source_name = 'crossref'

    def _by_doi(self, doi: str) -> Union[Tuple[str, str], None]:
        if not doi:
            return None

        url_encoded_doi = urllib.parse.quote_plus(doi)
        url = 'https://api.crossref.org/works/{}'.format(url_encoded_doi)

        response = requests.get(url)
        if not response.ok:
            self.logger.warning('Request error returns response: {}'.format(response.__dict__))
            return None

        response = response.json()

        if 'abstract' in response['message'] and response['message']['abstract']:
            return self.source_name, response['message']['abstract']

        return None

    def _by_title(self, title: str) -> Union[Tuple[str, str], None]:
        if not title:
            return None

        url_encoded_title = urllib.parse.quote_plus(title)
        url = 'https://api.crossref.org/works?rows=1&query.bibliographic={}'.format(url_encoded_title)

        response = requests.get(url)
        if not response.ok:
            self.logger.warning('Request error returns response: {}'.format(response.__dict__))
            return None

        response = response.json()

        doi = None
        if 'items' in response['message']:
            for item in response['message']['items']:
                if title.lower() == item['title'][0].lower():
                    doi = item['DOI']

        return self._by_doi(doi)

