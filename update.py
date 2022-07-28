import os
import re
import pandas as pd

from tqdm import tqdm

from services.metadata import MetadataService

tqdm.pandas()

from services.rdf import RDFGraphService

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, 'data')
RDF_DUMP_PATH = os.path.join(DATA_DIR, 'rdf_dump.nt')
PAPERS_DUMP_PATH = os.path.join(DATA_DIR, 'orkg_papers.csv')
ORKG_COLUMNS = ['uri', 'title', 'doi']
PAPER_COLUMNS = ['uri', 'title', 'doi', 'abstract_source', 'abstract', 'processed_abstract']

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


# TODO: automatically download a new rdf dump and sanitize it.
# TODO: use ArgumentParser
# TODO: try to fetch abstracts for existing papers with missing data ?


def sanitize_rdf_dump(path: str):
    """
    Sanitizes the RDF dump provided by ``path`` by removing corrupted lines and overwrites the corrupted version
    with the sanitized one.

    :param path: path to the RDF dump.
    """
    with open(path, 'r', encoding='utf-8') as f:
        dump = f.readlines()

    dump = [line for line in dump if not line.endswith('<null> .\n')]

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(dump)


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

    print('Parsing the RDF dump from {}'.format(RDF_DUMP_PATH))
    rdf_service = RDFGraphService(RDF_DUMP_PATH, sanitize_fun=sanitize_rdf_dump)

    # all orkg papers
    print('Querying ORKG...')
    orkg_df = rdf_service.query(SELECT).to_dataframe(columns=ORKG_COLUMNS)

    # the papers we have already fetched their abstracts
    if not os.path.exists(PAPERS_DUMP_PATH):
        pd.DataFrame(columns=PAPER_COLUMNS).to_csv(PAPERS_DUMP_PATH, index=False)

    print('Reading the papers dump from {}'.format(PAPERS_DUMP_PATH))
    papers_df = pd.read_csv(PAPERS_DUMP_PATH)
    print(papers_df.abstract_source.value_counts())

    # find those papers who exist in the orkg but do not in the papers dump
    new_papers_df = pd.concat(
        [
            orkg_df,
            papers_df.loc[:, orkg_df.columns].fillna('')
        ]
    ).drop_duplicates(keep=False)

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
