FROM ubuntu:16.04
MAINTAINER Francesco Favero <favero@cbs.dtu.dk>
RUN apt-get update && apt-get install -y r-base pypy samtools bowtie2
ADD exec/sequenza-utils /usr/local/bin/sequenza-utils
ADD exec/install_sequenza.R /usr/local/install_sequenza.R
RUN Rscript /usr/local/install_sequenza.R && rm /usr/local/install_sequenza.R
#RUN wget https://bitbucket.org/ffavero/sequenza_docker/raw/23e7559e7591fa12631647d775c8e10271989b25/exec/install_sequenza.R
#RUN wget https://bitbucket.org/ffavero/sequenza_docker/raw/23e7559e7591fa12631647d775c8e10271989b25/exec/sequenza-utils
#RUN mv sequenza-utils /usr/local/bin/sequenza-utils
#RUN Rscript install_sequenza.R && rm install_sequenza.R

