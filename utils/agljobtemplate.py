#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import jinja2
import ConfigParser
import urlparse
import ast


def get_extension(path):
    return path.split('.')[-1]


def parse_cfg_file(template_path, cfg_file, build_type):
    url_file_path = template_path + '/config/' + cfg_file
    try:
        with open(url_file_path):
            cfg = ConfigParser.ConfigParser()
            cfg.read(url_file_path)
            return cfg.items(build_type), cfg.get('infra', 'style')
    except IOError as err:
        raise err


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
    except (ConfigParser.NoSectionError) as err:
        str_err = "'--callback-to {}': must correspond to a section [{}] in the file '{}.cfg'".format(
            kci_callback, kci_callback, lava_callback)
        raise ConfigParser.NoSectionError(str_err)
    except (IOError) as err:
        str_err = "\n'--callback-from {}': must correspond to a file located in: ".format(lava_callback)
        str_err += "[releng-scripts]/templates/callback/{}.cfg".format(lava_callback)
        raise IOError(err, str_err)


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
            raise ImportError("Please make sure your version of jinja2 is >= 2.9")
        self._template_path = os.path.normpath(path)
        if not (os.path.isdir(self._template_path) and os.access(self._template_path, os.F_OK)):
            raise OSError("Cannot access {}".format(self._template_path))

        if self.machines is None:
            raise RuntimeError("No machine directory found at {}".format(self._template_path))

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

    def render_job(self, machine, url=None, url_branch=None, url_version=None,
                   job_name="AGL-short-smoke", priority="medium", tests=[], rfs_type=None,
                   lava_callback=None, kci_callback=None,
                   rfs_image=None, kernel_image=None, dtb_image=None, modules_image=None,
                   build_type=None,
                   build_version=None):

        if machine not in self.machines:
            raise RuntimeError("{} is not a available machine".format(machine))

        # Populate jinja substitution dict
        job = {}
        job['name'] = job_name
        job['yocto_machine'] = machine
        job['priority'] = priority
        job['build_type'] = build_type

        defaults, infra = parse_cfg_file(self._template_path, 'default.cfg', build_type)

        # If the user doesn't specify an URL, use the default one from the build-type
        if url is None:
            if infra == 'AGL':
                url_base = ''
                for section in defaults:
                    if section[0] == "urlbase":
                        url_base = section[1]
                # If not set, create a build_version from other args
                if (not build_version) and (url_branch) and (url_version):
                    build_version = 'AGL-' + build_type + '-' + url_branch + '-' + url_version

                url_fragment = ''
                if (build_type != 'default'):
                    url_fragment += url_branch + '/' + url_version + '/'

                if (machine == 'm3ulcb') or (machine == 'porter'):
                    url_fragment += machine + '-nogfx'
                else:
                    url_fragment += machine

                if (build_type != 'ci'):
                    url_fragment += '/deploy/images/' + machine

                url = urlparse.urljoin(url_base, url_fragment)

        test_templates = []
        # If the user doesn't specify tests, use the default ones from the build-type
        if not tests:
            if infra == 'AGL':
                for section in defaults:
                    if section[0] == "test_plan":
                        tests = ast.literal_eval(section[1])

        if 'all' in tests:
            tests = self.tests
        for t in tests:
            if t in self.tests:
                test_templates.append(os.path.join(self.TESTS_DIR, t + '.jinja2'))
            else:
                raise RuntimeError("{} is not an available test".format(t))

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
