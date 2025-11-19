FROM python:3.14-alpine AS baseimage

ENV TZ="UTC"
ENV USERNAME="flask_user"
ENV UID="1666"
ENV GROUPNAME="flask_user"
ENV GID="1666"
ENV UV_PYTHON_DOWNLOADS=0
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV DEBUG=0
ENV APP_DIR="/app"
ENV PYTHON_VENV_DIR="${APP_DIR}/.venv"
ENV PYTHON_EXEC="${PYTHON_VENV_DIR}/bin/python"

RUN set -eux \
    && apk add --no-cache --update --virtual .build-deps \
        build-base \
        linux-headers \
        ca-certificates \
        gcc \
        musl-dev \
        python3-dev \
        uv \
        git \
    && rm -rf /var/cache/* \
    && mkdir /var/cache/apk \
    && ln -sf /lib/ld-musl-x86_64.so.1 /usr/bin/ldd \
    && ln -s /lib /lib64 \
    && grep -q -E "^${GROUPNAME}:" /etc/group && echo "group '${GROUPNAME}' exists" || addgroup -g ${GID} -S ${GROUPNAME} \
    && grep -q -E "^${USERNAME}:" /etc/passwd && echo "user '${USERNAME}' exists" || adduser ${USERNAME} \
        --disabled-password \
        --gecos "Flask-JSONRPC User" \
        --ingroup ${GROUPNAME} \
        --uid ${UID} \
        -s /bin/false \
        ${USERNAME}

WORKDIR ${APP_DIR}
COPY --chown=${USERNAME}:${GROUPNAME} uv.lock pyproject.toml LICENSE.txt README.md ${APP_DIR}/

RUN set -eux \
    && uv venv \
    && uv sync --locked --no-dev --no-default-groups --group production

ARG VERSION=1
RUN echo "Version: ${VERSION}"
COPY --chown=${USERNAME}:${GROUPNAME} run.py src/ ${APP_DIR}/

RUN set -eux \
    && apk del .build-deps

ENV PATH="${PYTHON_VENV_DIR}/bin:${PATH}"
EXPOSE 5000

USER ${USERNAME}:${GROUPNAME}
CMD ["gunicorn", "lms.wsgi:app", "--bind", "0.0.0.0:5000"]
