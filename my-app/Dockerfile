FROM python:3.12.9-alpine3.21
RUN mkdir /opt/my-app
WORKDIR /opt/my-app
COPY ./app.py ./requirements.txt .
RUN \
  apk add --no-cache build-base exiv2-dev && \
  pip3 install -r requirements.txt && \
  apk --no-cache del build-base exiv2-dev && \
  apk --no-cache add exiv2
CMD ["python3", "app.py"]
LABEL org.opencontainers.image.source=https://github.com/castorw/techtalk-k8s-202503