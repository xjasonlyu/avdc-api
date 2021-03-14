FROM xjasonlyu/python-dlib:latest

COPY . /

RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt

LABEL org.opencontainers.image.source="https://github.com/xjasonlyu/AVDC"

EXPOSE 5000

ENTRYPOINT ["python", "/main.py"]
