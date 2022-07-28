import logging
from datetime import datetime
from typing import Tuple, Union

from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, MetadataReader, oai_dc_reader

from services import BaseMetadataService


class OAIService(BaseMetadataService):
    """
    The OAIService is intended to query information from the an OAI-Interface that follows the OAI-PMH protocol.
    NOTE: This service is currently only adapted to fetch paper abstracts data.

    The service follows the singleton pattern.
    """
    REGISTRY_URL = 'https://getinfo.tib.eu/oai/intern/repository/tib'

    def __init__(self, format='ftx'):
        """
        Returns a singleton instance of this service.

        :param format: the metadata format to fetch.
        """
        self.logger = logging.getLogger(__name__)
        super().__init__(self.logger)

        self.format = format

        registry = MetadataRegistry()
        registry.registerReader(self.format, self._create_reader())

        self.client = Client(self.REGISTRY_URL, registry)
        self.source_name = 'internal_oai'

    def _by_doi(self, doi: str) -> Union[Tuple[str, str], None]:
        return self._query(dynamic_set='identifier', query=doi)

    def _by_title(self, title: str) -> Union[Tuple[str, str], None]:
        return self._query(dynamic_set='title', query=title)

    def _query(self, dynamic_set: str, query: str) -> Union[Tuple[str, str], None]:
        if not query:
            return None

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
            return None

        if len(tupled_records) > 1:
            self.logger.warning('multiple records found, taking the most recent ftxCreated one for {}={}'
                                .format(dynamic_set, query))
            tupled_records.sort(key=lambda x: datetime.fromisoformat(x[0]), reverse=True)

        # joining the list of abstracts coming from one record
        return self.source_name, ' '.join(tupled_records[0][1])

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
