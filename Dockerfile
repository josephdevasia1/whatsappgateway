FROM python:3.9-slim as base

ENV \
    # Keeps Python from generating .pyc files in the container
    PYTHONDONTWRITEBYTECODE=1 \
    # Turns off buffering for easier container logging 
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN \
    apt-get -y update && apt-get install && \
    apt install git --no-install-recommends -y && \
    pip install -U poetry

FROM base as builder

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY whatsappcloudapigateway whatsappcloudapigateway
VOLUME "/data"
EXPOSE 8080

CMD ["uvicorn", "whatsappcloudapigateway.routes:app", "--port", "8080"]
