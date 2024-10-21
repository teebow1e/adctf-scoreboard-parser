FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Europe/Moscow

RUN apt-get update && \
    apt-get install -y \
    python3-pip

RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:saiarcot895/chromium-beta -y
RUN apt install chromium-browser -y

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "parser.py"]

