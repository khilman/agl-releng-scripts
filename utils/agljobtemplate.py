#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import jinja2
import ConfigParser
import urlparse


def get_extension(path):
    return path.split('.')[-1]

def parse_url_file(template_path, url_file, url_type):
    url_file_path = template_path + '/URLs/' + url_file
    try:
        with open(url_file_path):
            cfg = ConfigParser.ConfigParser()
            cfg.read(url_file_path)
            return cfg.get(url_type, 'urlbase'), cfg.get('infra', 'style')
    except IOError:
        raise IOError, "Unable to read from file {}".format(url_file_path)

def parse_callback_file(template_path, lava_callback, kci_callback):
    callback_file_path = template_path + '/callback/' + lava_callback + '.cfg'
    try:
        with open(callback_file_path):
            cfg = ConfigParser.ConfigParser()
            cfg.read(callback_file_path)
            if kci_callback is None:
                kci_callback = cfg.get('default', 'section')
            cb_data = dict(cfg.items(kci_callback))
            return cb_data
    except ConfigParser.NoSectionError:
        str_err = "Please make sure: --callback-to " + kci_callback
        str_err += " is correct and corresponds to a section in: "
        str_err += lava_callback + ".cfg"
        raise ConfigParser.NoSectionError, str_err
    except IOError:
        raise IOError, "Unable to read from file {}".format(callback_file_path)


class Agljobtemplate(object):

    DEFAULT_PATH = "templates"
    CALLBACK_DIR = "callback"
    MACHINES_DIR = "machines"
    TESTS_DIR = "tests"
    RFS_TYPE = ['nbd', 'ramdisk']

    def __init__(self, path=DEFAULT_PATH):
        try:
            from jinja2 import select_autoescape
        except ImportError:
            raise ImportError, "Please make sure your version of jinja2 is >= 2.9"
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

    def render_job(self, url, machine, url_branch=None, url_version=None,
                   job_name="AGL-short-smoke", priority="medium", tests=[], rfs_type=None,
                   lava_callback=None, kci_callback=None,
                   rfs_image=None, kernel_image=None, dtb_image=None, modules_image=None,
                   build_version=None):
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

        if url[:4] != 'http':
            # If not a full url, read from config file
            url_base, infra = parse_url_file(self._template_path, 'default.cfg', url)
            if infra == 'AGL':
                # If not set, create a build_version from other args
                if (not build_version) and (url_branch) and (url_version):
                    build_version = 'AGL-' + url + '-' + url_branch + '-' + url_version

                url_fragment = ''
                if (url != 'default'):
                    url_fragment += url_branch + '/' + url_version + '/'

                if (machine == 'm3ulcb') or (machine == 'porter'):
                    url_fragment += machine + '-nogfx'
                else:
                    url_fragment += machine

                if (url != 'ci'):
                    url_fragment += '/deploy/images/' + machine

                url = urlparse.urljoin(url_base, url_fragment)

        job['urlbase'] = url

        job['test_templates'] = test_templates

        if build_version is not None:
            job['kernel_version'] = build_version

        if rfs_type is not None:
            job['rootfs_type'] = rfs_type

        if rfs_image is not None:
            job['rfs_image'] = rfs_image

        if kernel_image is not None:
            job['kernel_image'] = kernel_image

        if dtb_image is not None:
            job['dtb'] = dtb_image

        if modules_image is not None:
            job['modules'] = modules_image

        if lava_callback:
            job['do_callback'] = True
            callback_data = parse_callback_file(self._template_path, lava_callback, kci_callback)
            job.update(callback_data)

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(self._template_path))
        env.filters['get_extension'] = get_extension
        template = env.get_template(os.path.join(self.MACHINES_DIR, machine + ".jinja2"))

        return template.render(job)
