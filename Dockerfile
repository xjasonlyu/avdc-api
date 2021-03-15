FROM xjasonlyu/python-dlib:latest
LABEL org.opencontainers.image.source="https://github.com/xjasonlyu/AVDC"

WORKDIR /AVDC
COPY . /AVDC

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

EXPOSE 5000

ENTRYPOINT ["python", "-m", "main", "--database", "/avdc.db"]
