#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import agljobtemplate
import argparse
import os


def parse_cmdline(machines, tests, rfs_types):
    parser = argparse.ArgumentParser(description="AGL create job",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', action='version', version='%(prog)s 1.0')
    parser.add_argument('--machine', action='store', choices=machines,
                        help="machine to generate the job for",
                        required=True)
    parser.add_argument('--priority', '-p', action='store', dest='priority',
                        help="job priority",
                        default='medium')
    parser.add_argument('--url', '-u', action='store', dest='url',
                        help="If using a custom URL specify it there. The files will be fetched from this URL.")
    parser.add_argument('--build-type', dest='build_type', action='store',
                        help="The type of build, can be one of: {'ci', 'daily', 'weekly', 'release'}.",
                        default="default")
    parser.add_argument('--branch', '--changeid', dest='url_branch', action='store',
                        help='The build branch (or changeid).')
    parser.add_argument('--version', '--patchset', dest='url_version', action='store',
                        help='The build version (or patchset).')
    parser.add_argument('--boot', action='store', dest='rfs_type',
                        choices=rfs_types, help='select boot type')
    parser.add_argument('--callback-from', action='store', dest='callback_from',
                        help='The LAVA lab (name) that will be responsible of doing the callback. '
                        'Please read: ./templates/callback/callback_readme.txt')
    parser.add_argument('--callback-to', action='store', dest='callback_to',
                        help='The KernelCI instance (name) that will receive the callback from LAVA. '
                        'Please read: ./templates/callback/callback_readme.txt')
    parser.add_argument('--test', dest='tests', action='store', choices=tests + ['all'],
                        help="add these test to the job", nargs='*', default=[])
    parser.add_argument('-o', '--output', dest='job_file', action='store',
                        help="destination file")
    parser.add_argument('-n', '--name', dest='job_name', action='store',
                        help="job name", default='AGL-short-smoke-wip')
    parser.add_argument('--rootfs-img', dest='rootfs_img', action='store',
                        help="The name of the root file system image (such as agl-demo-platform-raspberrypi3.ext4.xz)")
    parser.add_argument('--kernel-img', dest='kernel_img', action='store',
                        help="The name of the kernel to boot (such as uImage)")
    parser.add_argument('--dtb-img', dest='dtb_img', action='store',
                        help="The name of the dtb to use (such as uImage-bcm2710-rpi-3-b.dtb)")
    parser.add_argument('--modules-img', dest='modules_img', action='store',
                        help="The name of the modules to use (such as modules.tar.xz)")
    parser.add_argument('--build-version', dest='build_version', action='store',
                        help="the version number of the build.")

    args = parser.parse_args()

    if (bool(args.callback_from) ^ bool(args.callback_to)):
        parser.error("To specify callbacks both '--callback-to' and '--callback-from' are mandatory.")

    if (args.build_type is not "default") and (args.url is None):
        if (not args.url_branch) or (not args.url_version):
            parser.error("when using '--build-type' either '--url' or '--branch' and '--version' arguments needs to be set.")

    return args


def main():
    img = None
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
    ajt = agljobtemplate.Agljobtemplate(templates_dir)
    args = parse_cmdline(ajt.machines, ajt.tests, ajt.rfs_types)

    job = ajt.render_job(url=args.url, url_branch=args.url_branch, url_version=args.url_version,
                         machine=args.machine, tests=args.tests, priority=args.priority,
                         rfs_type=args.rfs_type, job_name=args.job_name,
                         lava_callback=args.callback_from, kci_callback=args.callback_to,
                         rfs_image=args.rootfs_img,
                         kernel_image=args.kernel_img,
                         dtb_image=args.dtb_img,
                         modules_image=args.modules_img,
                         build_type=args.build_type,
                         build_version=args.build_version)

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
