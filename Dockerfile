FROM r-base:3.4.2
MAINTAINER Francesco Favero <favero@cbs.dtu.dk>
RUN apt-get update \
   && apt-get install -y --no-install-recommends \
      samtools \
      pypy \
      python \
   && rm -rf /var/lib/apt/lists/*

ADD exec/sequenza-utils /usr/local/bin/sequenza-utils
ADD exec/install_sequenza.R /usr/local/install_sequenza.R
RUN Rscript /usr/local/install_sequenza.R && rm /usr/local/install_sequenza.R
