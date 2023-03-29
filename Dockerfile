
# Use pre-built selenium-python base image
FROM umihico/aws-lambda-selenium-python:latest

# copy scraper code
COPY app/ ${LAMBDA_TASK_ROOT}/app

# install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    pip3 install -r ${LAMBDA_TASK_ROOT}/requirements.txt

ENV APP_VERSION=1.0.0

CMD ["app/main.handler"]
