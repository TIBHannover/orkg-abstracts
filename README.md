# ORKG Papers

This service uses the RDF dump of the ORKG to create papers dump, in which papers
are associated with their abstracts. The abstract data is fetched using the **TIB-OAI**
metadata registry interface, and therefore, is **NOT** allowed to be distributed externally.
The papers dump is stored in a ``csv`` data format which makes it easy to be loaded with
a ``pandas.DataFrame``.

## Direct Download

You can download the abstracts dump by clicking on 
[this link](TODO),
which you can also use for you downstream application to directly download the data without any authentication.

E.g.: 

```commandline
wget <the link here> -O orkg_papers.csv
```

## How to Run

### prerequisites

* ``python 3.7.1``
* ``poetry`` ([instructions](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions))

---------------------------

```commandline
git clone https://git.tib.eu/orkg/orkg-papers.git
cd orkg-papers
```

then create an ``.env`` file with proper environment variables as described below, finally run 
the service with executing:

```commandline
// only if your system uses another base python version
poetry env use <path-to-your-python3.7-interpreter> 

poetry install
poetry run python -m src.update
```

## Environment Variables
The following environment variables are required to run the service
and are defined in the `.env` file.

| Variable                | Description                                                             |
|-------------------------|-------------------------------------------------------------------------|
| ``ORKG_TRIPLE_STORE``   | URL to the ORKG triple store.                                           |
| ``DATA_DIRECTORY``      | Path to the directory in which the dump file will be/is already stored. |
