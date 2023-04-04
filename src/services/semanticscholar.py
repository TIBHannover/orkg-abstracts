import logging
import urllib.parse
import time

from typing import Tuple, Union, Dict, Optional

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
        super().__init__(self.logger, source_name='semanticscholar')

    @respect_rate_limits
    def _by_doi(self, doi: str) -> Optional[Dict[str, str]]:
        if not doi:
            return None

        url_encoded_doi = urllib.parse.quote_plus(doi)
        fields = ['abstract', 'fieldsOfStudy', 's2FieldsOfStudy', 'publicationVenue', 'publicationDate']
        url = 'https://api.semanticscholar.org/v1/paper/{}?fields={}'.format(url_encoded_doi, ','.join(fields))

        response = self._request(url)

        if not response:
            return None

        if response.get('publicationVenue') and response['publicationVenue'].get('name'):
            publisher = response['publicationVenue']['name']
        else:
            publisher = None

        output = {
            'abstract': response['abstract'] or '',
            'research_field': '<SEP>'.join(response['fieldsOfStudy'] or []),
            's2_research_field': '<SEP>'.join(
                [field['category'] for field in response['s2FieldsOfStudy'] or []]
            ),
            'publisher': publisher,
            'date': response.get('publicationDate')
        }

        if any(output.values()):
            return output

        return None

    @respect_rate_limits
    def _by_title(self, title: str) -> Optional[Dict[str, str]]:
        if not title:
            return None

        url_encoded_title = urllib.parse.quote_plus(title)
        fields = ['abstract', 'title', 'fieldsOfStudy', 's2FieldsOfStudy', 'publicationVenue', 'publicationDate']

        url = 'https://api.semanticscholar.org/graph/v1/paper/search?query={}&fields={}'.format(
            url_encoded_title, ','.join(fields))

        response = self._request(url)

        if not response:
            return None

        if 'data' in response:
            for paper in response['data']:
                if title.lower() == paper['title'].lower():

                    if paper.get('publicationVenue') and paper['publicationVenue'].get('name'):
                        publisher = paper['publicationVenue']['name']
                    else:
                        publisher = None

                    output = {
                        'abstract': paper['abstract'] or '',
                        'research_field': '<SEP>'.join(paper['fieldsOfStudy'] or []),
                        's2_research_field': '<SEP>'.join(
                            [field['category'] for field in paper['s2FieldsOfStudy'] or []]
                        ),
                        'publisher': publisher,
                        'date': paper.get('publicationDate')
                    }

                    if any(output.values()):
                        return output

        return None

