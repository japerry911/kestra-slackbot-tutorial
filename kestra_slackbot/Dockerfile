ARG VIRTUAL_ENV=/opt/venv
ARG PLATFORM=linux/amd64

# ---PYTHON_BASE stage---
FROM --platform=$PLATFORM python:3.11.10-slim AS python_base

RUN apt-get update -q \
    && useradd -ms /bin/bash japerry

WORKDIR /app

RUN pip install --upgrade pip setuptools --no-cache-dir

ARG GCP_PROJECT_ID
ENV GCP_PROJECT_ID=$GCP_PROJECT_ID

ARG PYTHONPATH=/app/src
ENV PYTHONPATH=$PYTHONPATH

ARG VIRTUAL_ENV
ENV VIRTUAL_ENV=$VIRTUAL_ENV

ARG SLACK_BOT_USER_ID
ENV SLACK_BOT_USER_ID=$SLACK_BOT_USER_ID

ARG SLACK_BOT_TOKEN
ENV SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN

ARG SLACK_SIGNING_SECRET
ENV SLACK_SIGNING_SECRET=$SLACK_SIGNING_SECRET

ARG KESTRA_API_TOKEN
ENV KESTRA_API_TOKEN=$KESTRA_API_TOKEN

ARG SLACK_APP_TOKEN
ENV SLACK_APP_TOKEN=$SLACK_APP_TOKEN

ARG SLACK_BOT_USER_ID
ENV SLACK_BOT_USER_ID=$SLACK_BOT_USER_ID

ARG KESTRA_TENANT_ID
ENV KESTRA_TENANT_ID=$KESTRA_TENANT_ID

ARG KESTRA_SERVER_URL
ENV KESTRA_SERVER_URL=$KESTRA_SERVER_URL

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=True

COPY kestra_slackbot/pyproject.toml kestra_slackbot/uv.lock ./

RUN python3 -m venv $VIRTUAL_ENV

RUN apt-get update -q \
    && apt-get install -qy \
    git \
    && pip install --upgrade --progress-bar=off pip wheel \
    && pip install setuptools \
    && pip install uv \
    && uv export --format requirements-txt --no-hashes > requirements.txt \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

COPY kestra_slackbot/ /app

EXPOSE 3000

CMD ["uv", "run", "python", "-u", "app.py"]
