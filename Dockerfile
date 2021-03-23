FROM xjasonlyu/face-recognition:latest
LABEL org.opencontainers.image.source="https://github.com/xjasonlyu/avdc-api"

WORKDIR /avdc-api
COPY . /avdc-api

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""

ENV AVDC_DB="/avdc.db"
ENV AVDC_TOKEN=""

ENV PORT=5000
ENTRYPOINT exec python -m main -p $PORT
