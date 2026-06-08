FROM grafana/grafana:10.3.1

USER root
RUN apk add --no-cache gettext

COPY datasource.yml.template /etc/grafana/provisioning/datasources/datasource.yml.template
COPY dashboard.yml /etc/grafana/provisioning/dashboards/dashboard.yml
COPY dashboards/kampusevent-red.json /var/lib/grafana/dashboards/kampusevent-red.json
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
