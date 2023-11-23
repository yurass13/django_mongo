###########
# BUILDER #
###########

FROM python:3.10-alpine as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY . .

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

FROM python:3.10-alpine
LABEL authors="Yury Stolpov"

RUN mkdir -p /home/app

RUN addgroup -S app && adduser -S app -G app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME

WORKDIR $APP_HOME

RUN apk update && apk add libpq
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . $APP_HOME

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

RUN chown -R app:app $APP_HOME

USER app

ENTRYPOINT ["/home/app/web/entrypoint.sh"]
