FROM jaegertracing/all-in-one:1.54 AS jaeger
FROM otel/opentelemetry-collector-contrib:0.96.0 AS collector
FROM nginx:1.25-alpine

RUN apk add --no-cache gettext wget

COPY --from=jaeger /go/bin/all-in-one-linux /usr/local/bin/jaeger-all-in-one
COPY --from=collector /otelcol-contrib /otelcol-contrib
COPY otel-collector-config.yaml /etc/otelcol/config.yaml
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
