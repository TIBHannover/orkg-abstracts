import os
import re
import pandas as pd

from tqdm import tqdm

from src.services import MetadataService
from src.services import RDFGraphService

tqdm.pandas()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, '../data')
PAPERS_DUMP_PATH = os.path.join(DATA_DIR, 'orkg_papers.csv')
ORKG_COLUMNS = ['uri', 'title', 'doi']
PAPER_COLUMNS = ['uri', 'title', 'doi', 'abstract_source', 'abstract', 'processed_abstract']
TRIPLE_STORE_URL = os.getenv('ORKG_TRIPLE_STORE')  # ''


SELECT = """
PREFIX orkgp: <http://orkg.org/orkg/predicate/>
PREFIX orkgc: <http://orkg.org/orkg/class/>

SELECT ?paper ?paper_title ?doi
    WHERE {
           ?paper rdf:type orkgc:Paper ;
                  rdfs:label ?paper_title .

           OPTIONAL { ?paper orkgp:P26 ?doi } .
    }
"""

# TODO: cronjob
# TODO: upload/download
# TODO: print statistics


def find_new_papers(new_df: pd.DataFrame, old_df: pd.DataFrame) -> pd.DataFrame:
    """
    Finds the difference between new_df and old_df --> mathematically new_df\old_df
    Note that both dataframes must have the same columns.

    :param new_df: lhs dataframe.
    :param old_df: rhs dataframe.
    """
    ds1 = set(map(tuple, new_df.values))
    ds2 = set(map(tuple, old_df.values))

    return pd.DataFrame(list(ds1.difference(ds2)), columns=new_df.columns)


def extend_row_with_abstract(row: pd.Series) -> pd.Series:
    """
    Adds abstract columns to the given pd.Series.

    :param row: pd.Series representing a row.
    """
    metadata_service = MetadataService()

    abstract_source, abstract = metadata_service.query(doi=row['doi'], title=row['title'])

    row['abstract_source'] = abstract_source
    row['abstract'] = abstract
    row['processed_abstract'] = process_abstract(abstract)

    return row


def process_abstract(text: str) -> str:
    """
    removes HTML tags and strips white characters.

    :param text: the txt to be processed.
    """
    if not text:
        return text

    html_regex = '<.*?>'
    return ' '.join(re.sub(html_regex, ' ', text).split()).lower()


def main():

    # all orkg papers
    print('Querying ORKG...')
    rdf_service = RDFGraphService(url=TRIPLE_STORE_URL)
    orkg_df = rdf_service.query(SELECT, n_columns=len(ORKG_COLUMNS)).to_dataframe(columns=ORKG_COLUMNS)

    # the papers we have already fetched their abstracts
    if not os.path.exists(PAPERS_DUMP_PATH):
        pd.DataFrame(columns=PAPER_COLUMNS).to_csv(PAPERS_DUMP_PATH, index=False)

    print('Reading the papers dump from {}'.format(PAPERS_DUMP_PATH))
    papers_df = pd.read_csv(PAPERS_DUMP_PATH)
    print(papers_df.abstract_source.value_counts())

    # find those papers who exist in the orkg but do not in the papers dump
    new_papers_df = find_new_papers(orkg_df, papers_df.loc[:, orkg_df.columns].fillna(''))

    # try to fetch abstracts for new incoming papers
    if new_papers_df.empty:
        print('Nothing to update. Abort!')
        exit()
    else:
        print('Updating the papers dump...')
        new_papers_df = new_papers_df.progress_apply(extend_row_with_abstract, axis=1)

    # update the papers dump
    print('Dumping to {}'.format(PAPERS_DUMP_PATH))
    papers_df = pd.concat([papers_df, new_papers_df])
    papers_df.to_csv(PAPERS_DUMP_PATH, index=False)
    print(papers_df.abstract_source.value_counts())

    for value in papers_df.abstract_source.unique():
        path = '{}_{}.csv'.format(
            os.path.join(DATA_DIR, os.path.splitext(os.path.basename(PAPERS_DUMP_PATH))[0]),
            value
            )
        value_paper_df = papers_df[papers_df.abstract_source == value]
        value_paper_df.to_csv(path, index=False)


if __name__ == '__main__':
    main()
