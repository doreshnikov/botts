FROM python:latest
LABEL authors="jetbrains"
LABEL service="invoker"

USER root

WORKDIR /home
COPY ./invoker.py /home/invoker.py

ENTRYPOINT [ "python", "invoker.py" ]