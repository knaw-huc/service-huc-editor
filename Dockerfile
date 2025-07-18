FROM python:3.12.3-bookworm

ARG VERSION=0.1.10

RUN apt-get update &&\
	apt-get -y dist-upgrade &&\
	apt-get -y install vim

RUN useradd -ms /bin/bash huc

USER huc
WORKDIR /home/huc
ENV PYTHONPATH=/home/huc/huc-editor-service:/home/huc/huc-editor-service/data
ENV BASE_DIR=/home/huc/huc-editor-service
ENV BASE_URL=${BASE_URL:-"http://localhost:1210"}

RUN curl -sSL https://install.python-poetry.org | python -

RUN mkdir dev
ADD pyproject.toml dev/pyproject.toml
ADD README.md dev/README.md
ADD conf dev/conf
ADD data dev/data
ADD logs dev/logs
ADD resources dev/resources
ADD src dev/src
ADD tests dev/tests

RUN cd dev && \
    ${HOME}/.local/share/pypoetry/venv/bin/poetry install && \
    ${HOME}/.local/share/pypoetry/venv/bin/poetry update && \
    ${HOME}/.local/share/pypoetry/venv/bin/poetry build

RUN cp dev/dist/*.* .
#
RUN mkdir -p ${BASE_DIR}  && \
    pip install --no-cache-dir *.whl && rm -rf *.whl && \
    tar xf huc_editor_service-${VERSION}.tar.gz -C ${BASE_DIR} --strip-components 1

WORKDIR ${BASE_DIR}

CMD ["python", "src/main.py"]