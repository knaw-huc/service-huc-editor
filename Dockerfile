FROM python:3.12.3-bookworm

ARG VERSION=0.1.10

RUN apt-get update &&\
	apt-get -y dist-upgrade vim 

#RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN pip install uv

RUN useradd -ms /bin/bash huc

USER huc
WORKDIR /home/huc
ENV PYTHONPATH=/home/huc/huc-editor-service:/home/huc/huc-editor-service/data
ENV BASE_DIR=/home/huc/huc-editor-service
ENV BASE_URL=${BASE_URL:-"http://localhost:1210"}

RUN mkdir -p ${BASE_DIR}
WORKDIR ${BASE_DIR}

ADD pyproject.toml ${BASE_DIR}/pyproject.toml
ADD README.md ${BASE_DIR}/README.md
ADD conf ${BASE_DIR}/conf
ADD data ${BASE_DIR}/data
ADD logs ${BASE_DIR}/logs
ADD resources ${BASE_DIR}/resources
ADD src ${BASE_DIR}/src
ADD tests ${BASE_DIR}/tests
ADD uv.lock ${BASE_DIR}/uv.lock
USER root
RUN chown -R huc:huc ${BASE_DIR}
#RUN touch ${BASE_DIR}/logs/huc-editor-service.log
USER huc
       
ENV UV_COMPILE_BYTECODE=1

RUN uv sync --frozen --no-dev

ENV PATH="${BASE_DIR}/.venv/bin:$PATH"

ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "1210", "--workers", "4"]