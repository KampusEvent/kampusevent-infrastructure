FROM prom/prometheus:v2.49.1

USER root

COPY prometheus.yml.template /etc/prometheus/prometheus.yml.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
