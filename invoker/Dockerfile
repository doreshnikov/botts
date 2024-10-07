FROM python:3.12.7-bookworm
LABEL authors="doreshnikov"
LABEL service="invoker"

USER root

WORKDIR /home/botts
COPY .. /home/botts

RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get -y upgrade \
    && apt-get -y update \
    && apt-get -y install build-essential libcap-dev libsystemd-dev git

RUN git clone https://github.com/ioi/isolate.git
RUN make --directory=./isolate/ install

RUN pip3 install PyYAML

ENTRYPOINT [ "python3.12", "-m", "invoker.runners.mp" ]
