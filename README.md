## Sequenza Docker

Workflow
________

Add some data to a folder in the host:

```
ls -1 input/
    subset.fa.gz
    subset.gc50.gz
    testnorm.bam
    testtum.bam
```

Mount the folder in docker

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


# TODO

Dockstore/cwl/wdl
