FROM node:22-alpine AS build
WORKDIR /app
RUN corepack enable

# Build context is the repo root (pnpm needs the root lockfile)
COPY . .
RUN pnpm install --frozen-lockfile --filter web...

ARG NEXT_PUBLIC_SITE_URL
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_SITE_URL=$NEXT_PUBLIC_SITE_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN pnpm --filter web build

FROM node:22-alpine AS run
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# --chown matters: the server runs as `node` and writes its page cache
# (.next/cache and re-rendered pages). Files copied without it belong to root,
# and the home page's 60-second review refresh silently fails.
COPY --from=build --chown=node:node /app/web/.next/standalone ./
COPY --from=build --chown=node:node /app/web/.next/static ./web/.next/static
COPY --from=build --chown=node:node /app/web/public ./web/public

USER node
EXPOSE 3000
CMD ["node", "web/server.js"]