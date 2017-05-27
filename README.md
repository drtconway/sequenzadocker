<img src="https://bytebucket.org/sequenza_tools/icons/raw/d052aca4367bf5033bd5b8cf404320ec22f01202/svg/sequenza_tools/sequenzaalpha.svg" width="150" height="150">

![build_status](https://img.shields.io/docker/build/sequenza/sequenza.svg)
![docker_pulls](https://img.shields.io/docker/pulls/sequenza/sequenza.svg)
![docker_builds](https://img.shields.io/docker/automated/sequenza/sequenza.svg)

**Sequenza workflow**

Allele-specific SCNA analysis from tumor/normal sequencing with the sequenza docker container

*Dockstore*

Use this sample [sequenza_cwl.json](https://bitbucket.org/sequenza_tools/sequenza_docker/raw/4d5571f6bb07ba0d99789973efab44723118605a/sequenza_cwl.json) with public URLs for sample data.

```
   $ dockstore tool launch --entry registry.hub.docker.com/sequenza/sequenza  --json sequenza_cwl.json
```


*Interactive in Docker*

Add some data to a folder in the host:

```
ls -1 input/
    subset.fa.gz
    subset.gc50.gz
    testnorm.bam
    testtum.bam
```

Mount the folder in docker

(It is possible to mount also an output folder, but on OSX I had permission problems)

```
docker run -ti \
   -v `pwd`/input:/input \
   sequenza:latest bash

```

Look around
```
ls /input

sequenza-pipeline --help
```

Run the pipeline in docker

```
sequenza-pipeline \
       --sample-id test_seq_doc \
       --normal-bam  /input/testnorm.bam \
       --tumor-bam /input/testtum.bam \
       --reference-gz /input/subset.fa.gz
```

results in the /home/docker/*

*Building*

You need Docker installed in order to perform this build.

```
cd sequenza_docker
docker build -t sequenza .
```
