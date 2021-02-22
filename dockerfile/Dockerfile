ARG PLATFORM_TAG

FROM "quay.io/pypa/${PLATFORM_TAG}"

ARG PYTHON_ABI_TAG
ARG PYWHLOBF_VERSION
ARG PYWHLOBF_PLATFORM_TAG

ENV PYTHONIOENCODING=UTF-8 \
    LC_CTYPE=C.UTF-8 \
    LANG=C.UTF-8 \
    FIXUID_USER=pywhlobf \
    FIXUID_GROUP=pywhlobf \
    PYWHLOBF_PLATFORM_TAG=${PYWHLOBF_PLATFORM_TAG} \
    PYTHON_BIN="/opt/python/"${PYTHON_ABI_TAG}"/bin"

# Fixuid.
RUN /usr/sbin/groupadd \
    --gid 1000 \
    "$FIXUID_GROUP" \
    && \
    /usr/sbin/useradd \
    --uid 1000 \
    --gid "$FIXUID_GROUP" \
    --shell /bin/bash \
    "$FIXUID_USER" \
    && \
    USER="$FIXUID_USER" \
    && \
    GROUP="$FIXUID_GROUP" \
    && \
    curl -SsL 'https://github.com/boxboat/fixuid/releases/download/v0.5/fixuid-0.5-linux-amd64.tar.gz' | tar -C /usr/local/bin -xzf - \
    && \
    chown root:root /usr/local/bin/fixuid \
    && \
    chmod 4755 /usr/local/bin/fixuid \
    && \
    mkdir -p /etc/fixuid \
    && \
    printf 'user: %s\ngroup: %s\n' "$FIXUID_USER" "$FIXUID_GROUP" > /etc/fixuid/config.yml

# Pywhlobf.
RUN "$PYTHON_BIN"/pip install -U pip \
    && \
    "$PYTHON_BIN"/pip install pywhlobf=="$PYWHLOBF_VERSION"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && \
    chmod 777 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
