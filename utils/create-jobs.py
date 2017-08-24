#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import jinja2
import random
import string

template_directory = 'templates'

def parse_cmdline(machines, tests):
    parser = argparse.ArgumentParser(description="AGL create job")
    parser.add_argument('--version', "-v", action='version', version='%(prog)s 1.0')
    parser.add_argument('machine',  action='store', choices=machines,
                        help='machine to generate the job for')
    parser.add_argument('--priority', '-p', action='store', dest='priority',
                        help='job priority',
                        default='medium')
    parser.add_argument('--urlbase', '-u', action='store', dest='urlbase',
                        help='url fetch base',
                        default='http://www.baylibre.com/pub/agl/ci')
    parser.add_argument('--id', '-i', action='store', dest='identifier',
                        help='id suffix',
                        default=None)
    parser.add_argument('--boot', action='store', dest='rfs_type',
                         choices=['nfs', 'nbd', 'ramdisk'], help='select boot type')
    parser.add_argument('--test', dest='tests',  action='store', choices=tests,
                        help='add these test to the job', nargs='*')
    return parser.parse_args()

def list_available_jinjas(d):
    if not (os.path.isdir(d) and os.access(d, os.F_OK)):
        return []
    l = [ os.path.splitext(os.path.basename(f))[0] for f in os.listdir(d) if f.endswith('.jinja2') ]
    return l

def main():
    machines = list_available_jinjas(os.path.join(template_directory, "machines"))
    tests = list_available_jinjas(os.path.join(template_directory, "tests"))
    alltests = list(tests)
    alltests.append('all')
    args = parse_cmdline(machines, alltests)

    if args.tests is not None and 'all' in args.tests:
        args.tests = tests

    if args.identifier is None:
        args.identifier = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    # Populate jinja substitution dict
    job = {}
    job['name'] = "AGL test template job for {} - ID {}".format(args.machine, args.identifier)
    job['yocto_machine'] = args.machine
    job['priority'] = args.priority
    job['urlbase'] = args.urlbase

    if args.tests is not None:
        job['test_templates'] =  [ os.path.join('tests', t + '.jinja2') for t in args.tests ]

    if args.rfs_type is not None:
        job['rootfs_type'] = args.rfs_type

    job_file = "agl-test-{}".format(args.machine)
    if args.identifier != '':
        job_file += "-" + args.identifier
    job_file += ".yaml"
    template_file = os.path.join("machines", args.machine + ".jinja2")

    # Maybe the template directory should be an argument too
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_directory))
    template = env.get_template(template_file )

    try:
        with open(os.path.abspath(job_file), 'w') as j:
            j.write(template.render(job))
    except IOError as e:
        print "{}: {}".format(e.strerror, cfgpath)
        exit(e.errno)
    else:
        print "Job written to: {}".format(os.path.relpath(job_file))

if __name__ == '__main__':
    main()
