FROM python:3.12-alpine as builder

RUN apk add --no-cache --update --virtual .build-deps \
        build-base \
        linux-headers \
        ca-certificates \
        python3-dev \
    && rm -rf /var/cache/* \
    && mkdir /var/cache/apk \
    && ln -sf /lib/ld-musl-x86_64.so.1 /usr/bin/ldd \
    && ln -s /lib /lib64

WORKDIR /svc

ARG VERSION=1
RUN echo "Version: ${VERSION}"

COPY requirements/* ./

RUN pip install pip wheel --upgrade \
    && pip wheel --wheel-dir=/svc/wheels -r base.txt -r production.txt

FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBUG=0

RUN apk add --no-cache --update \
    && rm -rf /var/cache/* \
    && mkdir /var/cache/apk \
    && ln -sf /lib/ld-musl-x86_64.so.1 /usr/bin/ldd \
    && ln -s /lib /lib64 \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

COPY --from=builder /svc /svc

RUN pip install pip setuptools wheel --upgrade \
    && pip install --no-index --find-links=/svc/wheels -r /svc/base.txt -r /svc/production.txt \
    && addgroup -S flask_user \
    && adduser \
        --disabled-password \
        --gecos "" \
        --ingroup flask_user \
        --no-create-home \
        -s /bin/false \
        flask_user

WORKDIR /app

ARG VERSION=1
RUN echo "Version: ${VERSION}"

COPY . /app/
RUN chown flask_user:flask_user -R /app

USER flask_user

EXPOSE 5000
CMD gunicorn src.lms:app --bind 0.0.0.0:5000
