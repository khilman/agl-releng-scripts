#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import agljobtemplate
import argparse
import urlparse
import os

def parse_cmdline(machines, tests, rfs_types):
    parser = argparse.ArgumentParser(description="AGL create job",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', '-v', action='version', version='%(prog)s 1.0')
    parser.add_argument('machine',  action='store', choices=machines,
                        help="machine to generate the job for")
    parser.add_argument('--priority', '-p', action='store', dest='priority',
                        help="job priority",
                        default='medium')
    parser.add_argument('--urlbase', '-u', action='store', dest='urlbase',
                        help="url fetch base",
                        default='https://download.automotivelinux.org/AGL/upload/ci/')
    parser.add_argument('--boot', action='store', dest='rfs_type',
                        choices=rfs_types, help='select boot type')
    parser.add_argument('--callback', action='store', dest='callback',
                        help='url to notify when job is done. Please read: ./templates/callback/callback_readme.txt')
    parser.add_argument('--test', dest='tests',  action='store', choices=tests + ['all'],
                        help="add these test to the job", nargs='*', default=[])
    parser.add_argument('-o', '--output', dest='job_file',  action='store',
                        help="destination file")
    parser.add_argument('-n', '--name', dest='job_name',  action='store',
                        help="job name", default='AGL-short-smoke-wip')
    parser.add_argument('-j', '--jobid', dest='job_id',  action='store',
                        help='job id for link creation: URLBASE/JOB_ID')
    parser.add_argument('-i', '--jobidx', dest='job_index',  action='store',
                        help='job index for link creation: URLBASE/JOB_ID/JOB_INDEX', default='1')
    parser.add_argument('--img-name', dest='img_name',  action='store',
                        help="img base name (such as agl-demo-platform) - require img_ext")
    parser.add_argument('--img-ext', dest='img_ext',  action='store',
                        help="img extension (such as ext4.xz) - require img_name")
    parser.add_argument('--build-version', dest='build_version',  action='store',
                        help="the version number of the AGL build.")

    args = parser.parse_args()

    if (not args.img_name) != (not args.img_ext):
        parser.error("--img-name and --img-ext require one another")

    return args


def main():
    img = None
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
    ajt = agljobtemplate.Agljobtemplate(templates_dir)
    args = parse_cmdline(ajt.machines, ajt.tests, ajt.rfs_types)

    if args.img_name:
        img = args.img_name + "-" + args.machine + "." + args.img_ext

    if args.tests is not None and 'all' in args.tests:
        args.tests = ajt.tests

    if args.job_id is not None:
        args.urlbase = urlparse.urljoin(args.urlbase, args.job_id + '/')
        args.job_name += ' - {}'.format(args.job_id)

        if args.job_index is not None:
            args.urlbase = urlparse.urljoin(args.urlbase, args.job_index)
            args.job_name += ' - {}'.format(args.job_index)

    job = ajt.render_job(args.urlbase, args.machine, tests=args.tests, priority=args.priority,
                         rfs_type=args.rfs_type, job_name=args.job_name, kci_callback=args.callback,
                         rfs_image=img, build_version=args.build_version)

    if args.job_file is None:
        print job
    else:
        try:
            with open(args.job_file, 'w') as j:
                j.write(job)
        except IOError as e:
            print "{}: {}".format(e.strerror, args.job_file)
            exit(e.errno)
        else:
            print "Job written to: {}".format(args.job_file)

if __name__ == '__main__':
    main()
