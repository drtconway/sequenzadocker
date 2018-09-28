FROM r-base:3.5.1
MAINTAINER Francesco Favero <francesco.favero@bric.ku.dk>
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libcurl4-openssl-dev libssl-dev \
       libxml2-dev \
       samtools \
       tabix \
       bwa \
       python python-dev python-setuptools python-pip \
    && rm -rf /var/lib/apt/lists/* \

ADD exec/sequenza-utils /usr/local/bin/sequenza-utils
ADD exec/install_sequenza.R /usr/local/install_sequenza.R
RUN Rscript /usr/local/install_sequenza.R && rm /usr/local/install_sequenza.R
