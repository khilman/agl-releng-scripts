#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import jinja2


def get_extension(path):
    return path.split('.')[-1]


class Agljobtemplate(object):

    DEFAULT_PATH = "templates"
    MACHINES_DIR = "machines"
    TESTS_DIR = "tests"
    RFS_TYPE = ['nfs', 'nbd', 'ramdisk']

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

    def render_job(self, url, machine, job_name="AGL-short-smoke", priority="medium", tests=[], rfs_type="nbd"):
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
        job['rootfs_type'] = rfs_type

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self._template_path))
        env.filters['get_extension'] = get_extension
        template = env.get_template(os.path.join(self.MACHINES_DIR, machine + ".jinja2"))

        return template.render(job)
