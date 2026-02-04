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

# ---- dependency files FIRST ----
ADD pyproject.toml ${BASE_DIR}/pyproject.toml
ADD uv.lock ${BASE_DIR}/uv.lock
ADD README.md ${BASE_DIR}/README.md

ENV UV_COMPILE_BYTECODE=1
# ENV UV_HTTP_TIMEOUT=120
# RUN pip install pycparser==2.22 cffi==1.17.1 weasyprint==66.0
RUN uv sync --frozen --no-dev

ENV PATH="${BASE_DIR}/.venv/bin:$PATH"

# ---- application code AFTER deps ----
ADD conf ${BASE_DIR}/conf
ADD data ${BASE_DIR}/data
ADD logs ${BASE_DIR}/logs
ADD resources ${BASE_DIR}/resources
ADD src ${BASE_DIR}/src
ADD tests ${BASE_DIR}/tests

USER root
RUN chown -R huc:huc ${BASE_DIR}
USER huc

# ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "1210", "--reload"]
# ENTRYPOINT ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "1210", "--workers", "4"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "1210",  "--workers", "4"]
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "1210",  "--reload"]