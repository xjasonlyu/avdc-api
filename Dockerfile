FROM xjasonlyu/python-dlib:latest
LABEL org.opencontainers.image.source="https://github.com/xjasonlyu/avdc-api"

WORKDIR /avdc-api
COPY . /avdc-api

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

ENV AVDC_DB="/avdc.db"
ENV AVDC_TOKEN=""

EXPOSE 5000
ENTRYPOINT ["python", "-m", "main"]
