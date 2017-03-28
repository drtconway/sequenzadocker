FROM r-base:3.3.3
MAINTAINER Francesco Favero <favero@cbs.dtu.dk>
RUN apt-get update \
   && apt-get install -y --no-install-recommends \
      libcurl4-openssl-dev \
      libxml2-dev \
      samtools \
      tabix \
      bwa \
      python python-setuptools python-pip\
      pypy \
   && rm -rf /var/lib/apt/lists/*

ADD exec/sequenza-utils /usr/local/bin/sequenza-utils
ADD exec/install_sequenza.R /usr/local/install_sequenza.R
RUN Rscript /usr/local/install_sequenza.R && rm /usr/local/install_sequenza.R
