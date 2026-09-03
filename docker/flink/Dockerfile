FROM flink:1.20.1

USER root

RUN apt-get update \
    && apt-get install -y python3 python3-pip unzip \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && pip3 install --no-cache-dir protobuf==4.25.3 \
    && mkdir -p /opt/flink/opt/python/pyflink-unpacked \
    && unzip -q /opt/flink/opt/python/pyflink.zip -d /opt/flink/opt/python/pyflink-unpacked \
    && chmod +x /opt/flink/opt/python/pyflink-unpacked/pyflink/bin/pyflink-udf-runner.sh \
    && rm -rf /var/lib/apt/lists/*

COPY lib/*.jar /opt/flink/lib/

ENV PYTHONPATH=/opt/flink/opt/python/pyflink-unpacked:/opt/flink/opt/python/py4j-0.10.9.7-src.zip
ENV PYFLINK_CLIENT_EXECUTABLE=/usr/bin/python3
ENV PYFLINK_PYTHON=/usr/bin/python3

USER flink
