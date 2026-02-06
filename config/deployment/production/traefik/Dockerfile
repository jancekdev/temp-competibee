FROM docker.io/traefik:3.6.7
RUN mkdir -p /etc/traefik/acme \
  && touch /etc/traefik/acme/acme.json \
  && chmod 600 /etc/traefik/acme/acme.json
COPY ./config/deployment/production/traefik/traefik.yml /etc/traefik
