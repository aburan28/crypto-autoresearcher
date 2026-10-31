ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ARG SOURCE_REVISION
LABEL org.opencontainers.image.revision=${SOURCE_REVISION}
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      g++ gcc libc6-dev python3 python3-boto3 ca-certificates procps util-linux \
    && rm -rf /var/lib/apt/lists/*
COPY payload/ /opt/study/
RUN python3 /opt/study/execution/image_build.py --source-revision "${SOURCE_REVISION}"
ENV PYTHONDONTWRITEBYTECODE=1
USER 1000:1000
WORKDIR /work
ENTRYPOINT ["python3", "/opt/study/execution/worker.py"]
