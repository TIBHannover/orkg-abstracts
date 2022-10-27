from typing import Tuple, Union, Dict

from src.util.singleton import SingletonService
from src.services.crossref import CrossrefService
from src.services.semanticscholar import SemanticscholarService


class Metadata:

    def __init__(self):
        self.abstract: str = None

    def is_complete(self):
        """
        Returns True when all class attributes are filled and False otherwise.
        """
        return all([Metadata.__getattribute__(self, attr) for attr in vars(self).keys()])

    def update(self, source_info: Union[Tuple[str, Dict[str, str]], None]):
        """
        Updates the class attributes based on the passed ``source_info`` dictionary. If a metadata field
        is not filled yet and is included in ``source_info``, the field will be filled accordingly.

        :param source_info: Tuple of the source_name and a dictionary of the metadata found by that source.
        """
        if not source_info:
            return

        attributes = [attr for attr in vars(self).keys() if not attr.endswith('_source')]
        for attr in attributes:

            if attr not in source_info[1]:
                continue

            value = source_info[1][attr]

            if value and not Metadata.__getattribute__(self, attr):
                Metadata.__setattr__(self, attr, value)
                Metadata.__setattr__(self, '{}_{}'.format(attr, 'source'), source_info[0])


class MetadataService(SingletonService):

    def __init__(self):
        self.sources = [
            CrossrefService(),
            SemanticscholarService()
        ]

    def query(self, doi: str = None, title: str = None) -> Metadata:
        """
        Tries to query a paper abstract given its ```doi`` and/or ``title`` from
        1. Crossref
        2. Semanticscholar
        It tries to fetch the information first by the doi and then by the title in case both
        are provided.

        Returns Metadata object with the values filled by the first source match. Note that each
        metadata attribute is associated with a field with the naming convention ``field_source``
        denoting the external source from which the field has been fetched.

        :param doi: paper doi.
        :param title: paper title.
        """
        if not doi and not title:
            return Metadata()

        metadata = Metadata()
        for key, value in {'doi': doi, 'title': title}.items():
            for source in self.sources:
                if metadata.is_complete():
                    break

                source_info = source.query(**{key: value})
                metadata.update(source_info)

        return metadata
