FROM flink:1.20.1

USER root

RUN apt-get update \
    && apt-get install -y python3 python3-pip \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

COPY lib/*.jar /opt/flink/lib/

USER flink
