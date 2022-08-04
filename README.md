# ORKG Papers

This service uses the RDF dump of the ORKG to create papers dump, in which papers
are associated with their abstracts. The abstract data is fetched using the **TIB-OAI**
metadata registry interface, and therefore, is **NOT** allowed to be distributed externally.
The papers dump is stored in a ``csv`` data format which makes it easy to be loaded with
a ``pandas.DataFrame``.

## How to Run

TODO:

## GitLab CI

TODO:

## Environment Variables
The following environment variables are required to run the service
and are defined in the `.env` file.

| Variable                | Description                   |
|-------------------------|-------------------------------|
| ``ORKG_TRIPLE_STORE``   | URL to the ORKG triple store. |
