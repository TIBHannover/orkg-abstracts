from typing import List, Callable, Union

import numpy as np
import pandas as pd

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from rdflib.query import Result

from src.util.singleton import SingletonService


class RDFGraphService(SingletonService):
    """
    The RDFGraphService is intended to query the RDG graph given by its path or
    the hosted triple store given by its url. If both are provided the triple store
    will be used.

    The service follows the singleton pattern.
    """

    def __init__(self, url: str = None, path: str = None, sanitize_fun: Callable = None, format='nt'):
        """
        Returns a singleton instance of this service.

        :param url: URL of the hosted triple store.
        :param path: path or url to the rdf dump.
        :param sanitize_fun: callable to sanitize the file provided by ```path`` before parsing it.
        :param format: Defaults to ``nt``. Format of the RDF dump file.
        :return: RDFGraphService instance.
        """
        if not url and not path:
            raise ValueError('Either url or path must be provided')

        if url:
            self._graph = SPARQLWrapper(url)

        elif path:
            if sanitize_fun:
                sanitize_fun(path)
            self._graph = Graph().parse(path, format=format)

        self.np_results = np.empty(shape=0)

    def query(self, sparql_query: str, n_columns: int = 1) -> 'RDFGraphService':
        """
        Returns the self instance of this class with self.np_results filled with
        the results of ``sparql_query`` as numpy array of the shape (n_rows, n_columns).

        :param sparql_query: The SPARQL query to be use.
        :param n_columns: number of output columns in sparql_query. Note that this information is important for
            calling a triple store.
        """
        self.np_results = self._query(sparql_query, n_columns)
        return self

    def to_dataframe(self, columns: List[str] = None) -> pd.DataFrame:
        """
        Converts the results of the latest query function call to a pandas.DataFrame.

        :param columns: the name of the dataframe columns.
        """
        if self.np_results.size == 0:
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(self.np_results, columns=columns)

    @staticmethod
    def _to_numpy(query_results: Union[dict, Result], n_columns: int) -> np.array:
        result = []

        if isinstance(query_results, dict):
            if len(query_results['results']['bindings']) == 0:
                return np.empty(shape=0)

            for row in query_results['results']['bindings']:
                columns = [column['value'] for column in row.values()]
                columns += [''] * (n_columns - len(columns))  # ensuring a unified shape across rows.
                result.append(columns)

        elif isinstance(query_results, Result):
            if not query_results or len(query_results) == 0:
                return np.empty(shape=0)

            for row in query_results:
                columns = []
                for column in row:
                    columns.append('' if not column else column.toPython())
                result.append(columns)

        return np.array(result)

    def _query(self, sparql_query: str, n_columns: int) -> np.array:
        if isinstance(self._graph, SPARQLWrapper):
            self._graph.setQuery(sparql_query)
            self._graph.setReturnFormat(JSON)
            return self._to_numpy(self._graph.query().convert(), n_columns)

        if isinstance(self._graph, Graph):
            return self._to_numpy(self._graph.query(sparql_query), n_columns)

        return np.empty(shape=0)
