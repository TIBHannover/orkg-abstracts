from typing import Union, Tuple

from src.util.singleton import SingletonService


class BaseMetadataService(SingletonService):
    """
    The BaseMetadataService is a class for mutual functionalities for any metadata service.
    """

    def __init__(self, child_logger):
        self.logger = child_logger

    def query(self, doi: str = None, title: str = None) -> Union[Tuple[str, str], None]:
        """
        query a paper abstract given its ```doi`` and/or ``title``.

        :param doi: paper doi.
        :param title: paper title.
        """

        try:
            if doi:
                self.logger.debug('Querying for "{}"'.format(doi))
                return self._by_doi(doi)

            if title:
                # ignore titles with less than 3 terms, since this cannot guarantee exact matching
                if len(title.split(' ')) < 3:
                    return None

                self.logger.debug('Querying for "{}"'.format(title))
                return self._by_title(title)
        except Exception as e:
            self.logger.error('Querying threw this exception: {}'.format(e.__dict__))

        return None

    def _by_doi(self, doi: str) -> Union[Tuple[str, str], None]:
        raise NotImplementedError

    def _by_title(self, title: str) -> Union[Tuple[str, str], None]:
        raise NotImplementedError
