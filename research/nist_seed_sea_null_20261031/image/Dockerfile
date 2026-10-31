# Iso Lab task image for the real-field SEA null (UID 1000, no shell entrypoint).
FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends pari-gp pari-seadata awscli ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --uid 1000 --create-home lab
COPY sea_null_shard.gp run_shard.sh /opt/sea-null/
RUN chmod 0755 /opt/sea-null/run_shard.sh
USER 1000
WORKDIR /home/lab
