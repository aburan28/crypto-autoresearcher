FROM debian:bookworm-slim@sha256:7c7b2c966bc9ee8cedfeef67e0e279108992c77681fa595db4a9d65c06ccc587

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends pari-gp=2.15.2-1 \
    && rm -rf /var/lib/apt/lists/* \
    && test "$(gp --version-short)" = "2.15.2"

WORKDIR /study
ENTRYPOINT ["gp", "-q"]
