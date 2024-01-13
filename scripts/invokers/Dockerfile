FROM python:latest
LABEL authors="jetbrains"
LABEL service="invoker"

USER root

WORKDIR /home
COPY ./invoker.py /home/invoker.py
RUN pip3 install PyYAML

ENTRYPOINT [ "python", "invoker.py" ]