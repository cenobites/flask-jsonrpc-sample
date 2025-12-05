FROM node:24-alpine AS baseimage

ENV TZ="UTC"
ENV USERNAME="flask_user"
ENV UID="1666"
ENV GROUPNAME="flask_user"
ENV GID="1666"
ENV APP_DIR="/app"


FROM baseimage AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR ${APP_DIR}

COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* .npmrc* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi


FROM baseimage AS builder
WORKDIR ${APP_DIR}
COPY --from=deps ${APP_DIR}/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1

RUN \
  if [ -f yarn.lock ]; then yarn run build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
  else echo "Lockfile not found." && exit 1; \
  fi


FROM baseimage AS runner
WORKDIR ${APP_DIR}

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid ${GID} ${GROUPNAME}
RUN adduser --system --uid ${UID} ${USERNAME}

COPY --from=builder ${APP_DIR}/public ${APP_DIR}/public

COPY --from=builder --chown=${USERNAME}:${GROUPNAME} ${APP_DIR}/.next/standalone ./
COPY --from=builder --chown=${USERNAME}:${GROUPNAME} ${APP_DIR}/.next/static ./_next/static

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
EXPOSE 3000

USER ${USERNAME}:${GROUPNAME}
CMD ["node", "server.js"]