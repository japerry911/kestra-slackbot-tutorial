#!/usr/bin/env bash

# ==============================================
# SUMMARY:
# This script facilitates the deployment of a Kestra Slack bot to Google Cloud Run
# 
# KEY FUNCTIONS:
# - docker:deploy - Builds & pushes Docker image with environment variables
# - run:deploy - Deploys the container to Google Cloud Run
# - deploy - Executes both docker:deploy and run:deploy
#
# USAGE:
#   ./run.sh [function_name]
#   ./run.sh deploy         # Full deployment process
#   
# ENVIRONMENT:
# - Supports local development via .env file when EXPORT_ENV=true
# ==============================================

set -eo pipefail

# TTY allocation disabled
TTY=""
if [[ ! -t 1 ]]; then
  TTY="-T"
fi

DC="${DC:-run}"

if [ "${EXPORT_ENV}" = "true" ]; then
  export $(grep -v '^#' .env | xargs)
  printf "Loaded env variables from .env\n"
fi

function docker:deploy() {
  docker build \
    --build-arg GCP_PROJECT_ID="$GCP_PROJECT_ID" \
    --build-arg SLACK_BOT_USER_ID="$SLACK_BOT_USER_ID" \
    --build-arg SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN" \
    --build-arg SLACK_SIGNING_SECRET="$SLACK_SIGNING_SECRET" \
    --build-arg KESTRA_API_TOKEN="$KESTRA_API_TOKEN" \
    --build-arg SLACK_APP_TOKEN="$SLACK_APP_TOKEN" \
    --build-arg SLACK_BOT_USER_ID="$SLACK_BOT_USER_ID" \
    --build-arg KESTRA_TENANT_ID="$KESTRA_TENANT_ID" \
    --build-arg KESTRA_SERVER_URL="$KESTRA_SERVER_URL" \
    -t kestra-slackbot-tutorial --target python_base -f kestra_slackbot/Dockerfile .
  docker tag kestra-slackbot-tutorial us-central1-docker.pkg.dev/$GCP_PROJECT_ID/kestra-slackbot-tutorial/kestra-slackbot-tutorial:latest
  docker push us-central1-docker.pkg.dev/$GCP_PROJECT_ID/kestra-slackbot-tutorial/kestra-slackbot-tutorial:latest
}

function run:deploy() {
  gcloud run deploy kestra-slackbot-tutorial \
    --image us-central1-docker.pkg.dev/$GCP_PROJECT_ID/kestra-slackbot-tutorial/kestra-slackbot-tutorial:latest \
    --platform managed \
    --region us-central1 \
    --port 3000 \
    --allow-unauthenticated
}

function deploy() {
  docker:deploy
  run:deploy
}

END_TIME_FORMAT=$"\n\Execution completed in %3lR"

time "${@:-help}"