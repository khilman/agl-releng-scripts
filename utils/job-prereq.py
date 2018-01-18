#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import agljobtemplate
import argparse
import os
import yaml

FILE_MAP = {
    "kernel",
    "dtb",
    "initrd",
    "nbdroot",
}

# Mapping for qemu between command line QEMU args and LAVA yaml template file names
FILE_MAP_QEMU = {
    "kernel": "kernel",
    "initrd": "ramdisk",
}


def parse_cmdline(machines):
    description = "Print to stdout the file names needed to create a LAVA job"
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', action='version', version='%(prog)s 1.0')
    parser.add_argument('--machine', action='store', choices=machines,
                        help="Machine to output the job prerequisites.",
                        required=True)
    parser.add_argument('--dtb', action='store_true')
    parser.add_argument('--kernel', action='store_true')
    parser.add_argument('--initrd', action='store_true')
    parser.add_argument('--nbdroot', action='store_true')
    parser.add_argument('--build-type', action='store', dest='build_type',
                        nargs=3,
                        help="The type of build. It defines the URL to upload to.",
                        required=True)

    args = parser.parse_args()
    return args


def main():
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../templates')
    ajt = agljobtemplate.Agljobtemplate(templates_dir)
    args = parse_cmdline(ajt.machines)

    job = ajt.render_job(build_type=args.build_type[0],
                         url_branch=args.build_type[1],
                         url_version=args.build_type[2],
                         machine=args.machine)
    job_yaml = yaml.load(job)
    if args.machine != "qemux86-64":
        for key in FILE_MAP:
            if getattr(args, key):
                    print job_yaml["actions"][0]["deploy"][key].get("url").split('/')[-1]
    else:
        for key in FILE_MAP_QEMU:
            if getattr(args, key):
                    print job_yaml["actions"][0]["deploy"]["images"][FILE_MAP_QEMU[key]].get("url").split('/')[-1]


if __name__ == '__main__':
    main()
