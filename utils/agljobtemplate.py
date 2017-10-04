#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import jinja2
import ConfigParser


def get_extension(path):
    return path.split('.')[-1]


def parse_callback_file(template_path, callback_file, job):
    callback_file_path = template_path + '/callback/' + callback_file + '.cfg'
    try:
        with open(callback_file_path):
            cfg = ConfigParser.ConfigParser()
            cfg.read(callback_file_path)
            job['backend_fqdn'] = cfg.get('default', 'backend_fqdn')
            job['lab_name'] = cfg.get('default', 'lab_name')
            job['lab_token'] = cfg.get('default', 'lab_token')
    except IOError:
        raise IOError, "Unable to read from file {}".format(callback_file_path)


class Agljobtemplate(object):

    DEFAULT_PATH = "templates"
    CALLBACK_DIR = "callback"
    MACHINES_DIR = "machines"
    TESTS_DIR = "tests"
    RFS_TYPE = ['nbd', 'ramdisk']

    def __init__(self, path=DEFAULT_PATH):
        self._template_path = os.path.normpath(path)
        if not (os.path.isdir(self._template_path) and os.access(self._template_path, os.F_OK)):
            raise OSError, "Cannot access {}".format(self._template_path)

        if self.machines is None:
            raise RuntimeError, "No machine directory found at {}".format(self._template_path)

    def __list_jinjas(self, directory):
        d = os.path.join(self._template_path, directory)
        return [os.path.splitext(os.path.basename(f))[0] for f in os.listdir(d) if f.endswith('.jinja2')]

    @property
    def machines(self):
        """ List the availables machines
        """
        return self.__list_jinjas(self.MACHINES_DIR)

    @property
    def tests(self):
        """ List the availables tests
        """
        return self.__list_jinjas(self.TESTS_DIR)

    @property
    def rfs_types(self):
        return self.RFS_TYPE

    def render_job(self, url, machine, job_name="AGL-short-smoke", priority="medium", tests=[], rfs_type=None,
                   kci_callback=None, rfs_image=None, build_version=None):
        test_templates = []

        if machine not in self.machines:
            raise RuntimeError, "{} is not a available machine".format(machine)

        for t in tests:
            if t in self.tests:
                test_templates.append(os.path.join(self.TESTS_DIR, t + '.jinja2'))
            else:
                raise RuntimeError, "{} is not an available test".format(t)

        # Populate jinja substitution dict
        job = {}
        job['name'] = job_name
        job['yocto_machine'] = machine
        job['priority'] = priority
        job['urlbase'] = url
        job['test_templates'] = test_templates

        if build_version is not None:
            job['kernel_version'] = build_version

        if rfs_type is not None:
            job['rootfs_type'] = rfs_type

        if rfs_image is not None:
            job['rfs_image'] = rfs_image

        if kci_callback:
            if test_templates:
                job['callback_name'] = 'lava/test'
            else:
                job['callback_name'] = 'lava/boot'
            parse_callback_file(self._template_path, kci_callback, job)

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self._template_path))
        env.filters['get_extension'] = get_extension
        template = env.get_template(os.path.join(self.MACHINES_DIR, machine + ".jinja2"))

        return template.render(job)
