FROM ubuntu:15.04
MAINTAINER Francesco Favero <favero@cbs.dtu.dk>
RUN apt-get update && apt-get install -y r-base pypy

