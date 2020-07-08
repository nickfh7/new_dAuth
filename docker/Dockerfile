FROM python:3.7-slim-buster

WORKDIR /usr/src/new_dAuth

COPY ../network/ ./network/
COPY ../dAuth/ ./dAuth/
COPY ./README ../setup.py ../keygen.py ./

RUN apt -y update
RUN apt -y upgrade
RUN apt -y install gcc
RUN apt -y install pkg-config
RUN apt -y install libsecp256k1-dev
RUN pip install -e .
RUN mkdir -p /home/root/.sawtooth/keys/
RUN python keygen.py private > /home/root/.sawtooth/keys/root.priv
RUN python keygen.py public > /home/root/.sawtooth/keys/root.pub

EXPOSE 13127 14127
