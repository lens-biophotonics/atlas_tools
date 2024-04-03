# use base image
FROM python:3.10.12-slim

# who am I
MAINTAINER Ludovico Silvestri

# copy files
COPY * /src

# install dependencies
RUN python3 -m pip install --upgrade pip && pip3 install -r /src/requirements.txt
