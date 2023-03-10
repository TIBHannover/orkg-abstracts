# ORKG Papers

This service uses the RDF triple store of the ORKG to create papers dump, in which papers
are associated with their abstracts. The abstract data is fetched from
[``semanticscholar``](https://www.semanticscholar.org/) and [``crossref``](https://www.crossref.org/)
metadata registries, and therefore, is allowed to be dealt with as their usage policies allow
(see [license](#license)).

## Data Format
The papers dump is stored in a ``csv`` data format which makes it easy to be loaded with
a ``pandas.DataFrame``. The dump has the following columns schema:

* ``uri``: Paper URI in the ORKG.
* ``title``: Paper's title.
* ``doi``: Paper's DOI (Digital Object Identifier).
* ``abstract_source``: Source from which the abstract has been fetched. Possible values are ``semanticscholar``,
``crossref`` or ``no_record`` in case no abstract has been found for the paper.
* ``abstract``: The abstract text exactly as we get from the sources.
* ``processed_abstract``: Processed abstract's text. 
  * HTML tags are removed.
  * Whitespace characters are removed.
  * Lowercase is obtained.

Example usage:

```python
import pandas as pd

df = pd.read_csv('path/to/the/dump')
print(df.head())
```
and the output will be 

```commandline
                                   uri                                              title                         doi  abstract_source                                           abstract                                 processed_abstract
0  http://orkg.org/orkg/resource/R3000  A model for contextual data sharing in smartph...  10.1108/ijpcc-06-2016-0030         crossref  <jats:sec>\n<jats:title content-type="abstract...  \n purpose \n the purpose of this paper is to ...
1  http://orkg.org/orkg/resource/R1013  Capsules of the diatomAchnanthidium minutissim...           10.7717/peerj.858  semanticscholar  Achnanthidium minutissimum is a benthic freshw...  achnanthidium minutissimum is a benthic freshw...
2  http://orkg.org/orkg/resource/R1000                                                NaN                         NaN        no_record                                                NaN                                                NaN
3  http://orkg.org/orkg/resource/R1020  Open Research Knowledge Graph: Towards Machine...                         NaN  semanticscholar  Despite improved findability of and access to ...  despite improved findability of and access to ...
4  http://orkg.org/orkg/resource/R2018                                                NaN                         NaN        no_record                                                NaN                                                NaN
```


## Direct Download

The latest versions of the file, including a changelog, can be found at https://orkg.org/files/.

You can download the abstracts dump directly by clicking on 
[this link](https://orkg.org/files/orkg_papers.csv),
which you can also use for you downstream application to directly download the data without any authentication.

E.g.: 

```commandline
wget <the link here> -O orkg_papers.csv
```

## How to Run

**NOTE**: In case you're running the service for the first time and your ``ORKG_PAPERS_HOST_DATA_DIRECTORY``
path is different from ``orkg-papers/data/``, we recommend to copy its content to your provided path, so that
you do not need to fetch the data from scratch. In case you are executing the script with docker-compose
you do not need to manually copy the data, since it is already configured if you set the 
[environment variables](#environment-variables) properly.

### Manual Run

#### prerequisites

* ``python >= 3.7.1``
* ``poetry`` ([instructions](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions))

```commandline
git clone https://gitlab.com/TIBHannover/orkg/orkg-abstracts.git
cd orkg-papers
```

then create an ``.env`` file with proper [environment variables](#environment-variables) and finally run 
the service with executing:

```commandline
// only if your system uses another base python version
poetry env use <path-to-your-python3.7-interpreter> 

poetry install
poetry run python -m src.update
```

---------------------------
### Docker-Compose
To mount the host data directory into the container's please consider setting the [environment variables](#environment-variables)
properly. 

```commandline
git clone https://gitlab.com/TIBHannover/orkg/orkg-abstracts.git
cd orkg-papers
docker-compose up
```

## Environment Variables
The following environment variables are required to run the service
and are defined in the `.env` file.

| Variable                              | Description                                                                                                                                         |
|---------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| ``ORKG_TRIPLE_STORE``                 | URL to the ORKG triple store.                                                                                                                       |
| ``ORKG_PAPERS_HOST_DATA_DIRECTORY``   | Path to the directory in which the dump file will be/is already stored.                                                                             |
| ``ORKG_PAPERS_DOCKER_DATA_DIRECTORY`` | Path to the directory in which the dump file will be/is already stored inside the docker container. Only required when running with Docker-Compose. |

## License
Since this service only aggregates data from different sources, we therefore rely on their data
licenses. Please check each of:
* [SemanticScholar API License Agreement](https://api.semanticscholar.org/license/).
* [Crossref Metadata License Information](https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-metadata-license-information/).
