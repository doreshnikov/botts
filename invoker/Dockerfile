FROM python:3.12.7-bookworm
LABEL authors="doreshnikov"
LABEL service="invoker"

USER root

WORKDIR /home
COPY . /home/invoker

RUN apt-get upgrade
RUN apt-get update
RUN apt-get -y install build-essential libcap-dev libsystemd-dev git

RUN git clone https://github.com/ioi/isolate.git
RUN make --directory=./isolate/ install

RUN pip3 install PyYAML

ENTRYPOINT [ "python3.12", "-m", "invoker.runners.mp" ]
