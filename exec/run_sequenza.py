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


def index_fa_gz(fa_gz, log):
    idx_genome = ['samtools', 'faidx', fa_gz]
    idx_genome = shlex.split(' '.join(map(str, idx_genome)))
    log.log.info('Index %s' % ' '.join(map(str, idx_genome)))
    idx_genome_proc = subprocess.Popen(idx_genome)
    idx_genome_proc.communicate()[0]
    code = idx_genome_proc.returncode
    if code > 0:
        log.log.warning('Index of %s returned code %s' % (fa_gz, code))
        if fa_gz.endswith('.gz'):
            fa = fa_gz[:-3]
            with open(fa, 'wt') as genome_fa:
                try:
                    log.log.info('Unzip %s to %s' % (fa_gz, fa))
                    with gzip.open(fa_gz, 'rt') as genome_fa_gz:
                        for line in genome_fa_gz:
                            genome_fa.write(line)
                except IOError:
                    log.log.warning('IOError while unzip %s' % fa_gz)
            log.log.info('Remove old %s' % fa_gz)
            rm = ['rm', '-f', fa_gz]
            rm = shlex.split(' '.join(map(str, rm)))
            log.log.info('Remove %s' % ' '.join(map(str, rm)))
            rm_proc = subprocess.Popen(rm)
            rm_proc.communicate()[0]

            log.log.info('Compress %s with bgzip' % fa)
            bgzip = ['bgzip', '-f', fa]
            bgzip = shlex.split(' '.join(map(str, bgzip)))
            log.log.info('Bgzip compress %s' % ' '.join(map(str, bgzip)))
            bgzip_proc = subprocess.Popen(bgzip)
            bgzip_proc.communicate()[0]
            idx_genome = ['samtools', 'faidx', fa_gz]
            idx_genome = shlex.split(' '.join(map(str, idx_genome)))
            log.log.info('Attemp #2 Index %s' % ' '.join(map(str, idx_genome)))
            idx_genome_proc = subprocess.Popen(idx_genome)
            idx_genome_proc.communicate()[0]


def setup_bams(tumor, normal, bam_path, profile_obj, log, wig):
    tumor_link = os.path.join(bam_path, 'tumor.bam')
    normal_link = os.path.join(bam_path, 'normal.bam')
    log.log.info('Symlink %s to %s' % (tumor, tumor_link))
    log.log.info('Symlink %s to %s' % (normal, normal_link))
    os.symlink(tumor, tumor_link)
    os.symlink(normal, normal_link)
    idx_tumor = ['samtools', 'index', tumor_link]
    idx_normal = ['samtools', 'index', normal_link]
    gc50_wig = ['sequenza-utils', 'gc_wiggle',
                '-f', profile_obj.files['genome_fa_gz'],
                '-o', profile_obj.files['genome_gc_wig'],
                '-w', 50]

    idx_tumor = shlex.split(' '.join(map(str, idx_tumor)))
    idx_normal = shlex.split(' '.join(map(str, idx_normal)))
    gc50_wig = shlex.split(' '.join(map(str, gc50_wig)))

    log.log.info('Index %s' % ' '.join(map(str, idx_tumor)))
    idx_tumor_proc = subprocess.Popen(idx_tumor)
    idx_tumor_proc.communicate()[0]
    log.log.info('Index %s' % ' '.join(map(str, idx_normal)))
    idx_normal_proc = subprocess.Popen(idx_normal)
    idx_normal_proc.communicate()[0]

    index_fa_gz(profile_obj.files['genome_fa_gz'], log)

    if wig is None:
        log.log.info('GC wig %s' % ' '.join(map(str, gc50_wig)))
        gc50_wig_proc = subprocess.Popen(gc50_wig)
        gc50_wig_proc.communicate()[0]
    else:
        log.log.info('Symlink %s to %s' % (
            wig, profile_obj.files['genome_gc_wig']))
        os.symlink(wig, profile_obj.files['genome_gc_wig'])
    return {'tumor': tumor_link, 'normal': normal_link}


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
    parser.add_argument('--output',  dest='output',
                        help='Output folder, default CWD.',
                        required=False)
    parser.add_argument('-x', '--x-heterozygous', dest='female',
                        help=('Flag to set when the X chromomeme '
                              'is heterozygous. eg: set it for '
                              'female genomes'), action='store_true')
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
    parser.add_argument('--home_data',  dest='home_data',
                        help='Set the data in user home instead of /data',
                        action='store_true')
    args = parser.parse_args()
    archive_res = not args.no_arch
    if args.output:
        if os.path.isdir(args.output):
            output_dir = args.output
            archive_res = False
        else:
            output_dir = os.getcwd()
    else:
        output_dir = os.getcwd()
    if args.mem:
        os.environ['PYPE_MEM'] = '%iG' % args.mem
    if args.ncpu:
        os.environ['PYPE_NCPU'] = '%i' % args.ncpu

    log_dir = os.path.join(output_dir, 'logs')
    log = ExtLog('run_sequenza', log_dir, level=logging.INFO)
    log.log.info('Output results in folder %s' % output_dir)
    use_profile = 'default'
    log.log.info('Use profile %s' % use_profile)
    profile = get_profiles({})[use_profile]

    ref_dict = {'genome_fa_gz': args.ref_gz}

    create_symlinks(ref_dict, profile, log)
    if args.home_data:
        data_dir = os.path.join(os.getcwd(), 'data')
        os.mkdir(data_dir)
    else:
        data_dir = '/data'
    bam_files = setup_bams(args.tumor_bam, args.normal_bam,
                           data_dir, profile, log, args.ref_gc_wig)

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
        pype_cmd.append('--x_heterozygous', 'True')

    pype_cmd = shlex.split(' '.join(map(str, pype_cmd)))
    log.log.info('Prepare pype command line:')
    log.log.info(' '.join(map(str, pype_cmd)))
    pype_proc = subprocess.Popen(pype_cmd)
    pype_proc.communicate()[0]

    if archive_res:
        sqz_part_file = os.path.join(
            output_dir, '%s_parts_seqz.tar.gz' % args.sample)
        log.log.info(
            'Create archive for seqz partial files in %s' % sqz_part_file)
        sqz_dir = os.path.join(output_dir, 'seqz')

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
            output_dir, '%s_seqz_bin.tar.gz' % args.sample)
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
            output_dir, '%s_sequenza.tar.gz' % args.sample), 'w:gz')
        sequenza_tar.add(
            os.path.join(output_dir, 'sequenza'), arcname='sequenza')
        sequenza_tar.close()
        log.log.info('Archive log directory %s' % log_dir)
        tar = tarfile.open(
            os.path.join(output_dir, '%s_logs.tar.gz' % args.sample), 'w:gz')
        tar.add(log_dir, arcname='logs')
        tar.close()
    else:
        log.log.info('Skip archive of results')
    log.log.info('Done')

if __name__ == '__main__':
    main()
