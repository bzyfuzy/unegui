FROM python:3.11-alpine

RUN apk add -U tzdata
ENV TZ=Asia/Ulaanbaatar
RUN cp /usr/share/zoneinfo/Asia/Ulaanbaatar /etc/localtime

WORKDIR /app

ENV CSVS_PATH="/app/datas/csvs"
ENV JSONS_PATH="/app/datas/jsons"
ENV DB_NAME="datasets"
ENV DB_URI="mongodb://192.168.1.14:37017"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN crontab /app/crontab

CMD ["crond", "-f"]