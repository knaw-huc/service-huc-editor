FROM python:3.12.3-bookworm

ARG VERSION=0.1.6

RUN useradd -ms /bin/bash huc


USER huc
WORKDIR /home/huc
ENV PYTHONPATH=/home/huc/huc-editor-service/src
ENV BASE_DIR=/home/huc/huc-editor-service

COPY ./dist/*.* .


#
RUN mkdir -p ${BASE_DIR}  && \
    pip install --no-cache-dir *.whl && rm -rf *.whl && \
    tar xf huc_editor_service-${VERSION}.tar.gz -C ${BASE_DIR} --strip-components 1


WORKDIR ${BASE_DIR}


CMD ["python", "src/main.py"]