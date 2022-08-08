FROM python:3.7 as requirements-stage
LABEL maintainer="Omar Arab Oghli <Omar.ArabOghli@tib.eu>"

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Splitting in two stages gets rid of poetry, as for now, since it's not required for the application itself.
FROM python:3.7
LABEL maintainer="Omar Arab Oghli <Omar.ArabOghli@tib.eu>"

ENV IS_DOCKER true

WORKDIR /orkg-papers

COPY --from=requirements-stage /tmp/requirements.txt /orkg-papers/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /orkg-papers/requirements.txt

COPY ./src /orkg-papers/src

# Copying the data is important for the first time in order to save time for fetching already fetched data.
COPY ${ORKG_PAPERS_HOST_DATA_DIRECTORY} ${ORKG_PAPERS_DOCKER_DATA_DIRECTORY}

CMD ["python", "-m", "src.update"]
