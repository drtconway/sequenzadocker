FROM r-base:3.4.4
MAINTAINER Francesco Favero <favero@cbs.dtu.dk>
RUN apt-get update \
   && apt-get install -y --no-install-recommends \
      samtools bwa tabix \
      pypy python \
      python-dev python-setuptools python-pip \
      build-essential \
   && rm -rf /var/lib/apt/lists/*

ADD exec/sequenza-utils /usr/local/bin/sequenza-utils
ADD exec/install_sequenza.R /usr/local/install_sequenza.R
RUN Rscript /usr/local/install_sequenza.R && rm /usr/local/install_sequenza.R
