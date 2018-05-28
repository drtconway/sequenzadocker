#!/usr/bin/env cwl-runner

class: CommandLineTool
id: sequenza_workflow
label: sequenza_workflow
cwlVersion: v1.0

dct:creator:
  '@id': http://orcid.org/0000-0003-3684-2659
  foaf:name: Francesco Favero
  foaf:mbox: francesco.favero@bric.ku.dk

requirements:
  - class: DockerRequirement
    dockerPull: sequenza:latest

hints:
  - class: ResourceRequirement
    coresMin: 4
    ramMin: 16384
    outdirMin: 512000

inputs:
  sample-id:
    type: string
    inputBinding:
      position: 1
      prefix: --sample-id
  normal-bam:
    type: File
    inputBinding:
      position: 2
      prefix: --normal-bam
  tumor-bam:
    type: File
    inputBinding:
      position: 3
      prefix: --tumor-bam
  normal-bam-index:
    type: ["null", File]
    inputBinding:
      position: 4
      prefix: --normal-bam-index
  tumor-bam-index:
    type: ["null", File]
    inputBinding:
      position: 5
      prefix: --tumor-bam-index
  reference:
    type: File
    inputBinding:
      position: 6
      prefix: --reference-gz
  gc_wig:
    type: ["null", File]
    inputBinding:
      position: 7
      prefix: --gc_wig
  bin:
    type: ["null", int]
    inputBinding:
      position: 8
      prefix: --bin
  mem:
    type: ["null", int]
    inputBinding:
      position: 9
      prefix: --mem
  ncpu:
    type: ["null", int]
    inputBinding:
      position: 10
      prefix: --ncpu
outputs:
  archives:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.tar.gz"

baseCommand: [/usr/bin/sequenza-pipeline]
doc: |
    ![](https://bytebucket.org/sequenza_tools/icons/raw/da034ccc8c1ab5f5f8e020402267bd3f2dd5d361/svg/sequenza_tools/sequenzaalpha_150.svg)

    ![build_status](https://img.shields.io/docker/build/sequenza/sequenza.svg)
    ![docker_pulls](https://img.shields.io/docker/pulls/sequenza/sequenza.svg)
    ![docker_builds](https://img.shields.io/docker/automated/sequenza/sequenza.svg)

    **Sequenza workflow**

    Allele-specific SCNA analysis from tumor/normal sequencing with the sequenza docker container

