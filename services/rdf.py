from typing import List, Callable

import numpy as np
import pandas as pd

from rdflib import Graph

from services import SingletonService


class RDFGraphService(SingletonService):
    """
    The RDFGraphService is intended to query the RDG graph given by its path while initiating an object.

    The service follows the singleton pattern.
    """

    def __init__(self, path: str, sanitize_fun: Callable = None, format='nt'):
        """
        Returns a singleton instance of this service.

        :param path: path or url to the rdf dump.
        :param sanitize_fun: callable to sanitize the file provided by ```path`` before parsing it.
        :param format: Defaults to ``nt``. Format of the RDF dump file.
        :return: RDFGraphService instance.
        """
        if sanitize_fun:
            sanitize_fun(path)

        self.graph = Graph().parse(path, format=format)
        self.np_results = np.empty(shape=0)

    def query(self, sparql_query: str) -> np.array:
        """
        Returns the results of the ``sparql_query`` as numpy array of the shape (n_rows, n_columns).

        :param sparql_query: The SPARQL query to be use.
        """
        query_result = self.graph.query(sparql_query)

        if not query_result or len(query_result) == 0:
            return np.empty(shape=0)

        result = []
        for row in query_result:
            columns = []
            for column in row:
                columns.append('' if not column else column.toPython())
            result.append(columns)

        self.np_results = np.array(result)
        return self

    def to_dataframe(self, columns: List[str] = None) -> pd.DataFrame:
        """
        Converts the results of the latest query function call to a pandas.DataFrame.

        :param columns: the name of the dataframe columns.
        """
        return pd.DataFrame(self.np_results, columns=columns)
