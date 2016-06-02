FROM r-base:latest
MAINTAINER Francesco Favero <favero@cbs.dtu.dk>
RUN apt-get update
   && apt-get install -y --no-install-recommends \
      samtools \
      tabix \
      pypy \
   && rm -rf /var/lib/apt/lists/*

ADD exec/sequenza-utils /usr/local/bin/sequenza-utils
ADD exec/install_sequenza.R /usr/local/install_sequenza.R
RUN Rscript /usr/local/install_sequenza.R && rm /usr/local/install_sequenza.R
