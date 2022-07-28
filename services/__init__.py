import logging
from typing import Type, Tuple, Union

# Root logger configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stdout = logging.StreamHandler()
stdout.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
stdout.setFormatter(formatter)

logger.addHandler(stdout)


def singleton(_):
    """
    This decorator can only be used above the __new__ function of a class. It's responsible for returning a pre-created
    instance of the respective class or create a new one, if not have happened before.

    :param _: The __new__ function.
    :return:
    """

    def apply_pattern(cls: Type, *args, **kwargs):
        # attention: *args and **kwargs must be included even if not used!
        if not hasattr(cls, 'instance'):
            cls.instance = super(cls.__class__, cls).__new__(cls)
        return cls.instance

    return apply_pattern


class SingletonService:
    """
    The SingletonService is intended to be inherited by any service that follows the singleton pattern.
    """
    @singleton
    def __new__(cls, *args, **kwargs):
        pass


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
                self.logger.info('Querying for "{}"'.format(doi))
                return self._by_doi(doi)

            if title:
                # ignore titles with less than 3 terms, since this cannot guarantee exact matching
                if len(title.split(' ')) < 3:
                    return None

                self.logger.info('Querying for "{}"'.format(title))
                return self._by_title(title)
        except Exception as e:
            self.logger.error('Querying threw this exception: {}'.format(e.__dict__))

        return None

    def _by_doi(self, doi: str) -> Union[Tuple[str, str], None]:
        raise NotImplementedError

    def _by_title(self, title: str) -> Union[Tuple[str, str], None]:
        raise NotImplementedError
