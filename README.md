
## <a name="huc-api-service-setting"></a>HuC Editor API Service Setting

_This part describes how to set up and use development environment for HuC Editor API Service._


Requirements
------------

The HuC API Service uses several Python frameworks:
* [Poetry](https://python-poetry.org/docs/). Package management is crucial in Python to ensure scripts and code run smoothly. A dependency manager like Python Poetry facilitates specifying, installing, and resolving external packages for projects.
* [FastAPI](https://fastapi.tiangolo.com/). As the name suggests, FastAPI is primarily used for rapidly creating API endpoints. It is a modern, high-performance web framework for building APIs with Python, designed for speed, ease of use, and automatic documentation generation. 
* [Dynaconf](https://pypi.org/project/dynaconf/). Dynaconf provides dynamic configuration for Python applications. It can read settings from various sources, including environment variables, files, configuration servers, vaults, and more.


It is assumed that you are working in a Mac OS X environment.

* [Brew](https://brew.sh), to install some of the other stuff: see [brew](https://docs.brew.sh/Installation), if you haven't installed it yet.
* [Git](https://github.com/join) (`brew install git`).
* [Docker](https://www.docker.com/) (`brew install docker`)
* [Poetry](https://python-poetry.org): (`brew install poetry` or `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -`.)


Settings
--------
The HuC Editor API Service uses Dynaconf to manage its settings. It splits into multiple toml files.
* settings.toml, contains the base settings
* .secrets.toml, contains all secrets

In the settings.toml file, configurations are divided into multiple environment sections: [default, development, testing, production]. The default settings are always loaded and typically include dynamic parts using @format. The development and production sections contain values specific to their respective environments.


The example below demonstrates how dynamic settings operate. The metadata directory varies depending on the current environment.
```toml
[default.keycloak]
    url="http://localhost:9090"
    realms="huc_editor"
    client_id="huc-auth"

[development.keycloak]
    url="https://keycloak.dansdemo.nl"
    realms="huc_editor"
    client_id="huc-auth"

[production.keycloakd]
    url="https://keycloak.dans.knaw.nl"
    realms="huc_editor"
    client_id="huc-auth"
```

Building HuC Editor API Service
-------------------------------

```
poetry install; poetry update; poetry build; docker build --platform linux/amd64 --no-cache -t ekoindarto/huc-editor-service:0.1.7 -f Dockerfile . ; docker run -v ./conf:/home/dans/huc-editor-service/conf -d -p 1210:1210 --name huc-editor-service ekoindarto/huc-editor-service:0.1.7
```


Notes: 

The image tag version must match the version specified in both the `pyproject.toml` file and the `ARG version` in the Dockerfile.
e.g.:

huc-editor-service:0.1.7:

pyproject.toml

    [tool.poetry]
    name = "huc-editor-service"
    version = "0.1.7"

Dockerfile
    
    FROM python:3.12.3-bookworm

    ARG VERSION=0.1.7


OpenAPI Specification
---------------------

The OpenAPI Specification for the HuC Editor Service can be found at the following URLs:
* https://huc-editor-service.labs.dansdemo.nl/docs
* https://huc-editor-service.labs.dansdemo.nl/redoc
* http://localhot:1210/docs
* http://localhost:1210/redocs


Testing
-------

**…/profile/\<id>**

**POST**


`curl -X 'POST' 'https://huc-editor-service.labs.dansdemo.nl/profile/clarin.eu:cr1:p_1653377925727' -H 'accept: application/json' -H 'Authorization: Bearer YOUR_API_KEY'
`