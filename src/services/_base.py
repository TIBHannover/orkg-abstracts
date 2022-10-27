import requests

from typing import Union, Tuple, Dict

from src.util.singleton import SingletonService


class BaseMetadataService(SingletonService):
    """
    The BaseMetadataService is a class for mutual functionalities for any metadata service.
    """

    def __init__(self, child_logger):
        self.logger = child_logger

    def query(self, **kwargs) -> Union[Tuple[str, Dict[str, str]], None]:
        """
        query a paper abstract given its ```doi`` and/or ``title``.

        :param kwargs: paper's doi and/or title.
        """

        try:
            if kwargs['doi']:
                self.logger.debug('Querying for "{}"'.format(kwargs['doi']))
                return self._by_doi(kwargs['doi'])

            if kwargs['title']:
                # ignore titles with less than 3 terms, since this cannot guarantee exact matching
                if len(kwargs['title'].split(' ')) < 3:
                    return None

                self.logger.debug('Querying for "{}"'.format(kwargs['title']))
                return self._by_title(kwargs['title'])
        except Exception as e:
            self.logger.error('Querying threw this exception: {}'.format(e.__dict__))

        return None

    def _request(self, url, params=None, headers=None, method='GET'):
        response = requests.request(url=url, params=params, headers=headers, method=method)

        if not response.ok:
            self.logger.warning('Request error returns response: {}'.format(response.__dict__))
            return None

        return response.json()

    def _by_doi(self, doi: str) -> Union[Tuple[str, Dict[str, str]], None]:
        raise NotImplementedError

    def _by_title(self, title: str) -> Union[Tuple[str, Dict[str, str]], None]:
        raise NotImplementedError
