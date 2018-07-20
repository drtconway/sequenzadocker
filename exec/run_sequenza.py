#!/usr/bin/env python2.7

import argparse
import os
import gzip
import shlex
import subprocess
import tarfile
import logging
from pype.modules.profiles import get_profiles
from pype.logger import ExtLog


def create_symlinks(ref_dict, profile, log):
    '''
    Practical function to create symbolic links
    to the input files corresponding in the
    profile.files list
    '''
    for key in ref_dict:
        log.log.info('Handle reference file: %s' % key)
        if ref_dict[key]:
            log.log.info('Symlink %s to %s' % (ref_dict[key],
                                               profile.files[key]))
            os.symlink(ref_dict[key], profile.files[key])



def prepare_tmp_dirs(tempdir, log, subdirs=['databases', 'data', 'runs']):
    if not os.path.isdir(tempdir):
        os.makedirs(tempdir)
    for subdir in subdirs:
        subdir_tmp = os.path.join('/tmp', subdir)
        subdir = os.path.join(tempdir, subdir)
        if not os.path.isdir(subdir):
            log.log.info('Prepare temporary folder %s' % subdir)
            os.mkdir(subdir)
            if subdir_tmp != subdir:
                if not os.path.exists(subdir_tmp):
                    log.log.info('Symlink temporary folder %s to %s' %
                                 (subdir, subdir_tmp))
                    os.symlink(subdir, subdir_tmp)
                else:
                    log.log.error('The temporary folder %s already exists' %
                                  subdir_tmp)



def check_returncode(process, title, command, log):
    if process.returncode == 0:
        log.log.info('%s with command %s succeeded' % (title, command))
    else:
        log.log.error('%s with command %s failed' % (title, command))
        raise Exception('Error while executing %s' % command)


def setup_bams(tumor, normal, tumor_bai, normal_bai,
               bam_path, profile_obj, log):

    tumor_link = os.path.join(bam_path, 'tumor.bam')
    normal_link = os.path.join(bam_path, 'normal.bam')
    tumor_bai_link = os.path.join(bam_path, 'tumor.bam.bai')
    normal_bai_link = os.path.join(bam_path, 'normal.bam.bai')
    log.log.info('Symlink %s to %s' % (tumor, tumor_link))
    log.log.info('Symlink %s to %s' % (normal, normal_link))
    os.symlink(tumor, tumor_link)
    os.symlink(normal, normal_link)
    idx_tumor = ['samtools', 'index', tumor_link]
    idx_normal = ['samtools', 'index', normal_link]

    idx_tumor = shlex.split(' '.join(map(str, idx_tumor)))
    idx_normal = shlex.split(' '.join(map(str, idx_normal)))

    if tumor_bai is None:
        log.log.info('Index %s' % ' '.join(map(str, idx_tumor)))
        idx_tumor_proc = subprocess.Popen(idx_tumor)
        idx_tumor_proc.communicate()[0]
        check_returncode(idx_tumor_proc, 'tumor bam index',
                         ' '.join(map(str, idx_tumor)), log)
    else:
        log.log.info('Symlink %s to %s' % (tumor_bai, tumor_bai_link))
        os.symlink(tumor_bai, tumor_bai_link)
    if normal_bai is None:
        log.log.info('Index %s' % ' '.join(map(str, idx_normal)))
        idx_normal_proc = subprocess.Popen(idx_normal)
        idx_normal_proc.communicate()[0]
        check_returncode(idx_normal_proc, 'normal bam index',
                         ' '.join(map(str, idx_normal)), log)
    else:
        log.log.info('Symlink %s to %s' % (normal_bai, normal_bai_link))
        os.symlink(normal_bai, normal_bai_link)

    return {'tumor': tumor_link, 'normal': normal_link}


def setup_ref_files(wig, bgzip_ref, profile_obj, log):

    idx_genome = ['samtools', 'faidx', profile_obj.files['genome_fa']]
    idx_genome2 = ['samtools', 'faidx', profile_obj.files['genome_fa_gz']]
    bgz_genome = ['bgzip', '-c', '-f', profile_obj.files['genome_fa']]

    gc50_wig = ['sequenza-utils', 'gc_wiggle',
                '-f', profile_obj.files['genome_fa'],
                '-o', profile_obj.files['genome_gc_wig'],
                '-w', 50]

    idx_genome = shlex.split(' '.join(map(str, idx_genome)))
    idx_genome2 = shlex.split(' '.join(map(str, idx_genome2)))
    bgz_genome = shlex.split(' '.join(map(str, bgz_genome)))
    gc50_wig = shlex.split(' '.join(map(str, gc50_wig)))
    def bgzip_fa(idx_genome2, bgz_genome, profile_obj, log):
        with open(profile_obj.files['genome_fa_gz'], 'wt') as genome_fa_gz:
            log.log.info('Bgzip %s to %s' % (
                profile_obj.files['genome_fa'],
                profile_obj.files['genome_fa_gz']))
            bgzip_genome_proc = subprocess.Popen(
                bgz_genome, stdout=genome_fa_gz)
            bgzip_genome_proc.communicate()[0]
            check_returncode(bgzip_genome_proc, 'genome.fa bgzip',
                             ' '.join(map(str, bgz_genome)), log)

    def uzip_fa(profile_obj, log):
        with open(profile_obj.files['genome_fa'], 'wt') as genome_fa:
            try:
                log.log.info('Unzip %s to %s' % (profile_obj.files['genome_fa_gz'],
                                                 profile_obj.files['genome_fa']))
                with gzip.open(profile_obj.files['genome_fa_gz'], 'rt') \
                        as genome_fa_gz:
                    for line in genome_fa_gz:
                        genome_fa.write(line)
            except IOError:
                log.log.warning('IOError while unzip %s' %
                                profile_obj.files['genome_fa_gz'])

    if bgzip_ref is True:
        bgzip_fa(idx_genome2, bgz_genome, profile_obj, log)
    else:
        uzip_fa(profile_obj, log)

    log.log.info('Index %s' % ' '.join(map(str, idx_genome2)))
    idx_genome2_proc = subprocess.Popen(idx_genome2)
    idx_genome2_proc.communicate()[0]
    genome_gz_fai = '%s.fai' % profile_obj.files['genome_fa_gz']
    if os.path.isfile(genome_gz_fai):
        bgzip_ref = False
    else:
        log.log.warning(('Failed to index genome.gz, '
                         'will attempt to recover by '
                         're-compressing with bgzip'))
        bgzip_ref = True

    log.log.info('Index %s' % ' '.join(map(str, idx_genome)))
    idx_genome_proc = subprocess.Popen(idx_genome)
    idx_genome_proc.communicate()[0]
    check_returncode(idx_genome_proc, 'genome.fa index',
                     ' '.join(map(str, idx_genome)), log)
    if bgzip_ref is True:
        os.unlink(profile_obj.files['genome_fa_gz'])
        bgzip_fa(idx_genome2, bgz_genome, profile_obj, log)
        log.log.info('Index %s' % ' '.join(map(str, idx_genome2)))
        idx_genome2_proc = subprocess.Popen(idx_genome2)
        idx_genome2_proc.communicate()[0]
        check_returncode(idx_genome2_proc, 'genome.fa.gz index',
                         ' '.join(map(str, idx_genome2)), log)
    if wig is None:
        log.log.info('GC wig %s' % ' '.join(map(str, gc50_wig)))
        gc50_wig_proc = subprocess.Popen(gc50_wig)
        gc50_wig_proc.communicate()[0]
        check_returncode(gc50_wig_proc, 'GC wiggle',
                         ' '.join(map(str, gc50_wig)), log)
    else:
        log.log.info('Symlink %s to %s' % (
            wig, profile_obj.files['genome_gc_wig']))
        os.symlink(wig, profile_obj.files['genome_gc_wig'])



def main():
    parser = argparse.ArgumentParser(
        description=('Run sequenza with bio_pype'))
    parser.add_argument('--sample-id',  dest='sample',
                        help='Sample id, identifier of the run',
                        required=True)
    parser.add_argument('--normal-bam', '-n',  dest='normal_bam',
                        help='Normal Bam file',  required=True)
    parser.add_argument('--tumor-bam', '-t',  dest='tumor_bam',
                        help='Tumor Bam file',  required=True)
    parser.add_argument('--normal-bam-index',  dest='normal_bai',
                        help='Normal Bam file',  required=False)
    parser.add_argument('--tumor-bam-index',  dest='tumor_bai',
                        help='Tumor Bam file',  required=False)
    parser.add_argument('--reference-gz', '-f', dest='ref_gz',
                        help=('Genome reference gz-compressed file '
                              '(or plain text)'),
                        required=True)
    parser.add_argument('--gc_wig', '-w', dest='ref_gc_wig',
                        help='GC-content wiggle files',
                        required=False)
    parser.add_argument('--bin',  dest='bin',
                        help=('Number of nt to use for binning '
                              'the final seqz file. Default: 50'),
                        default=50)
    parser.add_argument('--mem',  dest='mem',
                        help=('Amount of max GB of memory to use. '
                              'Default: autodetect'),
                        type=int, required=False)
    parser.add_argument('--ncpu',  dest='ncpu',
                        help='Number of cpu to use. Default: autodetect',
                        type=int, required=False)
    parser.add_argument('--breaks',  dest='breaks',
                        help=('Optional BED files defining the breakpoins '
                               '-instead of the built-in segmentation-'),
                        type=str, required=False)
    parser.add_argument('-x', '--x-heterozygous', dest='female',
                        help=('Flag to set when the X chromomeme '
                              'is heterozygous. eg: set it for '
                              'female genomes'), action='store_true')
    parser.add_argument('--store_seqztmp', dest='seqztmp',
                        help='Store temporary seqz files',
                        action='store_true')
    parser.add_argument('--ignore_normal', dest='ignore_normal',
                        help=('Use the GC-normalized tumor depth instead '
                              'of computing the depth-ratio vs the normal sample'),
                        action='store_true')
    parser.add_argument('--ratio_priority', dest='ratio_priority',
                        help=('Consider only the depth-ration (and not the B-allele '
                              'frequency) when fit the segments to a model'),
                        action='store_true')
    parser.add_argument('--cellularity', dest='cellularity', type=float,
                        help=('Run sequenza with a pre-defined cellularity '
                              'value. A number between 0 and 1'),
                        required=False)
    parser.add_argument('--ploidy', dest='ploidy', type=float,
                        help=('Run sequenza with a pre-defined ploidy '
                              'value. A number between 0.9 and 10, 2 for a '
                              'diploid genome'),
                        required=False)
    parser.add_argument('--cellularity-range', dest='cellularity_range',
                        type=str, metavar='0-1',
                        help=('Limit the cellularity search to a '
                              'given range. Two numbers each between 0 and 1'
                              'separated by "-". Default 0-1'),
                        default='0-1')
    parser.add_argument('--ploidy-range', dest='ploidy_range',
                        type=str, metavar='0.9-10',
                        help=('Limit the ploidy search to a '
                              'given range. Two numbers each between '
                              '0.9 and 10 separated by "-". Default 1-7'),
                        default='1-7')
    parser.add_argument('--no_archive',  dest='no_arch',
                        help='Set to avoid tar of output',
                        action='store_true')
    parser.add_argument('--tmp',  dest='tempdir',
                        help='Set the temporary folder',
                        default='/tmp')
    args = parser.parse_args()
    archive_res = not args.no_arch
    if args.mem:
        os.environ['PYPE_MEM'] = '%iG' % args.mem
    if args.ncpu:
        os.environ['PYPE_NCPU'] = '%i' % args.ncpu
    try:
        tempdir = os.environ['TEMPDIR']
    except KeyError:
        tempdir = args.tempdir

    log_dir = os.path.join(os.getcwd(), 'logs')
    log = ExtLog('run_sequenza', log_dir, level=logging.INFO)


    log.log.info('Prepare temporary diirectory structure')
    prepare_tmp_dirs(tempdir, log, ['databases', 'data', 'workdir'])

    output_dir = '/tmp/workdir'
    results_dir = os.getcwd()

    log.log.info('Output results in folder %s' % output_dir)
    use_profile = 'default'
    log.log.info('Use profile %s' % use_profile)
    profile = get_profiles({})[use_profile]

    if os.path.splitext(args.ref_gz)[1] == '.gz':
        ref_dict = {'genome_fa_gz': args.ref_gz}
        bgzip_ref = False
    else:
        ref_dict = {'genome_fa': args.ref_gz}
        bgzip_ref = True
    create_symlinks(ref_dict, profile, log)

    setup_ref_files(args.ref_gc_wig, bgzip_ref, profile, log)

    bam_files = setup_bams(args.tumor_bam, args.normal_bam,
                           args.tumor_bai, args.normal_bai,
                           '/tmp/data', profile, log)
    if args.breaks is not None:
        if args.breaks.endswith('.gz'):
            breaks_file = 'breaks.txt.gz'
        else:
            breaks_file = 'breaks.txt'
        breaks_link = os.path.join('/tmp/data', breaks_file)
        log.log.info('Symlink %s to %s' % (args.breaks, breaks_link))
        os.symlink(args.breaks, breaks_link)

    out_dirs = [os.path.join(output_dir, 'sequenza'),
                os.path.join(output_dir, 'seqz')]
    for out_dir in out_dirs:
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

    pype_cmd = ['pype', '--profile', use_profile, 'pipelines',
                '--queue', 'parallel', '--log', log_dir,
                'sequenza',
                '--sample_name', args.sample,
                '--tumor_bam', bam_files['tumor'],
                '--normal_bam', bam_files['normal'],
                '--seqz_out', os.path.join(
                    output_dir, 'seqz', '%s.seqz.gz' % args.sample),
                '--bin_size', args.bin,
                '--ncpu', args.ncpu,
                '--sequenza_out', os.path.join(
                    output_dir, 'sequenza', args.sample),
                '--cellularity', args.cellularity,
                '--ploidy', args.ploidy,
                '--cellularity_range', args.cellularity_range,
                '--ploidy_range', args.ploidy_range]
    if args.female is True:
        pype_cmd += ['--x_heterozygous', 'True']
    if args.ratio_priority is True:
        pype_cmd += ['--ratio_priority', 'True']
    if args.ignore_normal is True:
        pype_cmd += ['--ignore_normal', 'True']
    if args.breaks is not None:
        pype_cmd += ['--breaks', breaks_link]

    pype_cmd = shlex.split(' '.join(map(str, pype_cmd)))
    log.log.info('Prepare pype command line:')
    log.log.info(' '.join(map(str, pype_cmd)))
    pype_proc = subprocess.Popen(pype_cmd)
    pype_proc.communicate()[0]

    if archive_res:
        sqz_dir = os.path.join(output_dir, 'seqz')

        if args.seqztmp:
            sqz_part_file = os.path.join(
                results_dir, '%s_parts_seqz.tar.gz' % args.sample)
            log.log.info(
                'Create archive for seqz partial files in %s' % sqz_part_file)
            sqz_tar = tarfile.open(sqz_part_file, 'w:gz')
            for result in os.listdir(sqz_dir):
                result = os.path.join(sqz_dir, result)
                if os.path.isfile(result):
                    base_path, file_name = os.path.split(result)
                    if file_name.startswith('%s_part_' % args.sample):
                        log.log.info(
                            'Add %s to %s archive' % (result, sqz_part_file))
                        sqz_tar.add(result, arcname=file_name)
            sqz_tar.close()

        sqz_bin_file = os.path.join(
            results_dir, '%s_seqz_bin.tar.gz' % args.sample)
        log.log.info(('Create archive for seqz binned and '
                      'indexed files in %s') % sqz_bin_file)
        sqz_bin_res_name = '%s_bin%s.seqz.gz' % (args.sample, args.bin)
        sqz_bin_res = os.path.join(sqz_dir, sqz_bin_res_name)
        sqz_bin = tarfile.open(sqz_bin_file, 'w:gz')
        if os.path.isfile(sqz_bin_res):
            sqz_bin.add(sqz_bin_res, arcname=sqz_bin_res_name)
        else:
            log.log.info('File %s not found' % sqz_bin_res)
        if os.path.isfile('%s.tbi' % sqz_bin_res):
            sqz_bin.add(
                '%s.tbi' % sqz_bin_res,
                arcname='%s.tbi' % sqz_bin_res_name)
        else:
            log.log.info('File %s.tbi not found' % sqz_bin_res)
        sqz_bin.close()

        log.log.info('Archive sequenza results folder %s' %
                     os.path.join(output_dir, 'sequenza'))
        sequenza_tar = tarfile.open(os.path.join(
            results_dir, '%s_sequenza.tar.gz' % args.sample), 'w:gz')
        sequenza_tar.add(
            os.path.join(output_dir, 'sequenza'), arcname='sequenza')
        sequenza_tar.close()
        log.log.info('Archive log directory %s' % log_dir)
        tar = tarfile.open(
            os.path.join(results_dir, '%s_logs.tar.gz' % args.sample), 'w:gz')
        tar.add(log_dir, arcname='logs')
        tar.close()
    else:
        log.log.info('Skip archive of results')
    log.log.info('Done')

if __name__ == '__main__':
    main()
