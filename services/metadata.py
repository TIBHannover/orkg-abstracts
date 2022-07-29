from typing import Tuple

from services import SingletonService
from services.crossref import CrossrefService
from services.semanticscholar import SemanticscholarService


class MetadataService(SingletonService):

    def __init__(self):
        self.crossref = CrossrefService()
        self.semanticscholar = SemanticscholarService()

    def query(self, doi: str = None, title: str = None) -> Tuple[str, str]:
        """
        Tries to query a paper abstract given its ```doi`` and/or ``title`` from
        1. Crossref
        2. Semanticscholar
        3. Internal TIB-OAI interface
        It tries to fetch the information first by the doi and then by the title in case both
        are provided.

        Returns Tuple[abstract_src, abstract].

        :param doi: paper doi.
        :param title: paper title.
        """
        if not doi and not title:
            return 'no_record', ''

        response = self.crossref.query(doi=doi) or \
               self.semanticscholar.query(doi=doi) or \
               self.crossref.query(title=title) or \
               self.semanticscholar.query(title=title)

        if response:
            return response

        return 'no_record', ''
