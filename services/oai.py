from datetime import datetime
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, MetadataReader, oai_dc_reader

from services import SingletonService


class OAIService(SingletonService):
    """
    The OAIService is intended to query information from the an OAI-Interface that follows the OAI-PMH protocol.
    NOTE: This service is currently only adapted to fetch paper abstracts data.

    The service follows the singleton pattern.
    """

    def __init__(self, url, format='ftx'):
        """
        Returns a singleton instance of this service.

        :param url: the OAI-Interface url.
        :param format: the metadata format to fetch.
        """
        self.format = format

        registry = MetadataRegistry()
        registry.registerReader(self.format, self._create_reader())

        self.client = Client(url, registry)

    def query(self, doi: str = None, title: str = None) -> str:
        """
        query a paper abstract given its ```doi`` and/or ``title``.

        :param doi: paper doi.
        :param title: paper title.
        """
        return self._by_doi(doi) or self._by_title(title) or ''

    def _by_doi(self, doi: str) -> str:
        return self._query(dynamic_set='identifier', query=doi)

    def _by_title(self, title: str) -> str:
        # ignore titles with less than 3 terms, since this cannot guarantee exact matching
        if len(title.split(' ')) < 3:
            return ''

        return self._query(dynamic_set='title', query=title)

    def _query(self, dynamic_set: str, query: str) -> str:
        if not query:
            return ''

        records = self.client.listRecords(
            metadataPrefix=self.format,
            set='collection~*_solr~{}:"{}"'.format(dynamic_set, query)
        )

        tupled_records = []  # List[Tuple[creation_date, List[abstracts]]]
        for i, record in enumerate(records):
            if record[1]._map['abstracts']:
                tupled_records.append(
                    (
                        record[1]._map['creation_date'][0],
                        record[1]._map['abstracts']
                    )
                )

        if len(tupled_records) == 0:
            print('WARNING: no record found for {}={}'.format(dynamic_set, query))
            return ''

        if len(tupled_records) > 1:
            print('WARNING: multiple records found, taking the most recent ftxCreated one for {}={}'
                  .format(dynamic_set, query))
            tupled_records.sort(key=lambda x: datetime.fromisoformat(x[0]), reverse=True)

        # joining the list of abstracts coming from one record
        return ' '.join(tupled_records[0][1])

    def _create_reader(self) -> MetadataReader:
        return {
            'ftx': self._create_ftx_reader(),
            'oai_dc': oai_dc_reader
        }[self.format]

    @staticmethod
    def _create_ftx_reader() -> MetadataReader:
        return MetadataReader(
            fields={
                'creation_date': ('textList', 'ftx:documentContainer/x:document/x:systemInfo/x:ftxCreationDate/text()'),
                'abstracts': (
                    'textList', 'ftx:documentContainer/x:document/x:bibliographicInfo/x:abstracts/x:abstract/text()'),
            },
            namespaces={
                'x': 'http://www.openarchives.org/OAI/2.0/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'ftx': 'http://www.tib-hannover.de/ext/schema/2007-06-26/fiz-tib-schema.xsd'
            }
        )
