import logging
import urllib.parse
from typing import Dict, Optional

from src.services._base import BaseMetadataService


class CrossrefService(BaseMetadataService):
    """
    The CrossrefService fetches abstract information from Crossref API.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        super().__init__(self.logger, source_name='crossref')

        orkg_mail = 'info@orkg.org'
        self.params = {'mailto': orkg_mail}
        self.headers = {'User-Agent': 'ORKG-Abstracts/0.1.0 (https://www.orkg.org; mailto:{})'.format(orkg_mail)}

    def _by_doi(self, doi: str) -> Optional[Dict[str, str]]:
        if not doi:
            return None

        url_encoded_doi = urllib.parse.quote_plus(doi)
        url = 'https://api.crossref.org/works/{}'.format(url_encoded_doi)

        response = self._request(url, params=self.params, headers=self.headers)

        if not response:
            return None

        output = {
            'abstract': response['message'].get('abstract', ''),
            'research_field': '<SEP>'.join(response['message'].get('subject', [])),
            'publisher': response['message'].get('publisher', ''),
            'date': '<SEP>'.join(
                [str(part) for part in response['message'].get('issued', {}).get('date-parts', [''])[0]]
            )
        }

        if any(output.values()):
            return output

        return None

    def _by_title(self, title: str) -> Optional[Dict[str, str]]:
        if not title:
            return None

        url_encoded_title = urllib.parse.quote_plus(title)
        url = 'https://api.crossref.org/works?rows=1&query.bibliographic={}'.format(url_encoded_title)

        response = self._request(url, params=self.params, headers=self.headers)

        if not response:
            return None

        doi = None
        if 'items' in response['message']:
            for item in response['message']['items']:
                if title.lower() == item['title'][0].lower():
                    doi = item['DOI']

        return self._by_doi(doi)

