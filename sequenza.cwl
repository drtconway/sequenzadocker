#!/usr/bin/env cwl-runner

class: CommandLineTool
id: sequenza_workflow
label: sequenza_workflow
cwlVersion: v1.0

doc: |
    ![build_status](https://....)
    A workflow with the sequenza docker container

dct:creator:
  '@id': http://orcid.org/0000-0003-3684-2659
  foaf:name: Francesco Favero
  foaf:mbox: francesco.favero@bric.ku.dk

requirements:
  - class: DockerRequirement
    dockerPull: registry.hub.docker.com/sequenza/sequenza:latest

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
  reference-gz:
    type: File
    inputBinding:
      position: 4
      prefix: --reference-gz
  gc_wig:
    type: ["null", File]
    inputBinding:
      position: 5
      prefix: --gc_wig
  bin:
    type: ["null", int]
    inputBinding:
      position: 6
      prefix: --bin
  bin:
    type: ["null", int]
    inputBinding:
      position: 6
      prefix: --bin
  mem:
    type: ["null", int]
    inputBinding:
      position: 7
      prefix: --mem
  ncpu:
    type: ["null", int]
    inputBinding:
      position: 8
      prefix: --ncpu
outputs:
  archives:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.tar.gz"

baseCommand: [/usr/bin/sequenza-pipeline]

