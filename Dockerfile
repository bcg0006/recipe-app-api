# This Dockerfile is used to build a Docker image for a Python-based recipe app API.
# It sets up the necessary environment, installs dependencies, and configures the container.

FROM python:3.9-alpine3.13

# Maintainer of the Dockerfile
LABEL maintainer="bruno"

# Set the PYTHONUNBUFFERED environment variable to ensure that Python output is sent straight to the terminal
ENV PYTHONUNBUFFERED 1

# Copy the requirements files and the app code into the container
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app

# Set the working directory to /app
WORKDIR /app

# Expose port 8000 for the Django app
EXPOSE 8000

# Define an argument to determine if the development requirements should be installed
ARG DEV=false

# Create a Python virtual environment and install dependencies
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers &&\
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media  && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    chmod -R +x /scripts

# Add the Python binary path to the container's PATH environment variable
ENV PATH="/scripts:/py/bin:$PATH"

# Set the user to run the container as
USER django-user

CMD ["run.sh"]