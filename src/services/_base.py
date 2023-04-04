import requests

from typing import Union, Tuple, Dict, Optional

from src.util.singleton import SingletonService


class BaseMetadataService(SingletonService):
    """
    The BaseMetadataService is a class for mutual functionalities for any metadata service.
    """

    def __init__(self, child_logger, source_name):
        self.logger = child_logger
        self.source_name = source_name

    def query(self, **kwargs) -> Tuple[str, Optional[Dict[str, str]]]:
        """
        query a paper abstract given its ```doi`` and/or ``title``.

        :param kwargs: paper's doi and/or title.
        """

        try:
            response = None

            if 'doi' in kwargs and kwargs['doi']:
                self.logger.debug('Querying for "{}"'.format(kwargs['doi']))
                response = self._by_doi(kwargs['doi'])

            elif 'title' in kwargs and kwargs['title']:
                # ignore titles with less than 3 terms, since this cannot guarantee exact matching
                if len(kwargs['title'].split(' ')) < 3:
                    return self.source_name, None

                self.logger.debug('Querying for "{}"'.format(kwargs['title']))
                response = self._by_title(kwargs['title'])

            return self.source_name, response
        except Exception as e:
            self.logger.error('Querying threw this exception: {}'.format(e))

        return self.source_name, None

    def _request(self, url, params=None, headers=None, method='GET') -> Optional[dict]:
        response = requests.request(url=url, params=params, headers=headers, method=method)

        if not response.ok:
            self.logger.warning('Request error returns response: {}'.format(response.__dict__))
            return None

        return response.json()

    def _by_doi(self, doi: str) -> Union[Tuple[str, Dict[str, str]], None]:
        raise NotImplementedError

    def _by_title(self, title: str) -> Union[Tuple[str, Dict[str, str]], None]:
        raise NotImplementedError
