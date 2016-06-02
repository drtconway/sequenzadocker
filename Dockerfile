FROM debian:testing
MAINTAINER Francesco Favero <favero@cbs.dtu.dk>
RUN apt-get update && apt-get install -y r-base pypy samtools tabix
ADD exec/sequenza-utils /usr/local/bin/sequenza-utils
ADD exec/install_sequenza.R /usr/local/install_sequenza.R
RUN Rscript /usr/local/install_sequenza.R && rm /usr/local/install_sequenza.R
