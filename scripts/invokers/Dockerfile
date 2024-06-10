FROM python:latest
LABEL authors="doreshnikov"
LABEL service="invoker"

USER root

WORKDIR /home
COPY common.py /home/common.py
COPY invoker_mp.py /home/invoker_mp.py
COPY invoker_pi.py /home/invoker_pi.py
COPY invoker_iso.py /home/invoker_iso.py

RUN apt-get --upgrade
RUN apt-get update
RUN apt-get -y install build-essential libcap-dev libsystemd-dev git

RUN git clone git@github.com:ioi/isolate.git
RUN make --directory=./isolate/ install

RUN pip3 install PyYAML

ENTRYPOINT [ "python" ]