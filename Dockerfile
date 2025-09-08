FROM ghcr.io/astral-sh/uv:python3.12-alpine

ARG VERSION=0.1.10

#TODO: add vi(m)

RUN adduser -D -s /bin/bash huc

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

ENV UV_COMPILE_BYTECODE=1

RUN uv sync --frozen --no-dev

ENV PATH="${BASE_DIR}/.venv/bin:$PATH"

ENTRYPOINT ["uvicorn", "src/main.py", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "4"]