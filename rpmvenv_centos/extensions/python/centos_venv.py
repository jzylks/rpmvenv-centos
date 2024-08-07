"""Extension for packaging a Python virtualenv."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from confpy.api import Configuration
from confpy.api import ListOption
from confpy.api import Namespace
from confpy.api import StringOption
from confpy.api import BoolOption

from rpmvenv.extensions import interface


cfg = Configuration(
    python_centos_venv=Namespace(
        description='Generate RPMs from Python virtualenv.',
        source_venv=StringOption(
            description='Optional path for source virtualenv',
            required=False,
        ),
        cmd=StringOption(
            description='The executable to use for creating a venv.',
            default='virtualenv',
        ),
        flags=ListOption(
            description='Flags to pass to the venv during creation.',
            option=StringOption(),
            default=(),
        ),
        name=StringOption(
            description='The name of the installed venv.',
            required=True,
        ),
        path=StringOption(
            description='The path in which to install the venv.',
            default='/usr/share/python',
        ),
        python=StringOption(
            description='The python executable to use in the venv.',
            required=False,
        ),
        requirements=ListOption(
            description='Names of requirements files to install in the venv.',
            option=StringOption(),
            default=('requirements.txt',)
        ),
        pip_flags=ListOption(
            description='Flags to pass to pip during pip install calls.',
            option=StringOption(),
            default=(),
        ),
        strip_binaries=BoolOption(
            description='Whether to strip native modules of debug information '
                        'that often contains the buildroot paths',
            required=False,
            default=True,
        )
    ),
)


class Extension(interface.Extension):

    """Extension for packaging a Python virtualenv."""

    name = 'python_centos_venv'
    description = 'Packaging extension for generating virtualenv.'
    version = '1.0.0'
    requirements = {}

    @staticmethod
    def generate(config, spec):
        """Generate Python virtualenv content."""
        spec.macros['_build_id_links'] = 'none'
        if config.python_centos_venv.source_venv:
            spec.macros['venv_cmd'] = 'cp -r {0}'.format(config.python_centos_venv.source_venv)
        else:
            spec.macros['venv_cmd'] = '{0} {1}'.format(
                config.python_centos_venv.cmd,
                ' '.join(
                    config.python_centos_venv.flags if config.python_centos_venv.flags else ()
                ),
            )
            if config.python_centos_venv.python:

                spec.macros['venv_cmd'] = '{0} --python={1}'.format(
                    spec.macros['venv_cmd'],
                    config.python_centos_venv.python,
                )
        spec.macros['venv_name'] = config.python_centos_venv.name
        spec.macros['venv_install_dir'] = '{0}/%{{venv_name}}'.format(
            config.python_centos_venv.path,
        )
        spec.macros['venv_dir'] = '%{buildroot}/%{venv_install_dir}'
        spec.macros['venv_bin'] = '%{venv_dir}/bin'
        spec.macros['venv_python'] = '%{venv_bin}/python'
        spec.macros['venv_pip'] = (
            '%{{venv_python}} %{{venv_bin}}/pip install {0}'.format(
                ' '.join(
                    config.python_centos_venv.pip_flags
                    if config.python_centos_venv.pip_flags
                    else ()
                ),
            )
        )
        spec.macros['__prelink_undo_cmd'] = "%{nil}"

        spec.globals['__os_install_post'] = (
            "%(echo '%{__os_install_post}' | sed -e "
            "'s!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:"
            "]].*$!!g')"
        )

        spec.tags['AutoReq'] = 'No'
        spec.tags['AutoProv'] = 'No'
        spec.tags['BuildRequires'] = '/usr/bin/pathfix.py'

        spec.blocks.prep.append('mkdir -p %{buildroot}/%{venv_install_dir}')

        spec.blocks.files.append('/%{venv_install_dir}')

        if config.python_centos_venv.source_venv:
            spec.blocks.install.append('mkdir -p `dirname %{venv_dir}`')
        spec.blocks.install.append('%{venv_cmd} %{venv_dir}')
        spec.blocks.install.append('cd %{SOURCE0}')
 
        for requirement in config.python_centos_venv.requirements:

            spec.blocks.install.append(
                '%{{venv_pip}} -r %{{SOURCE0}}/{0}'.format(
                    requirement,
                )
            )

        spec.blocks.install.extend((
            'cd %{SOURCE0}',
            '%{venv_python} setup.py install',
            'cd -',
            '# RECORD files are used by wheels for checksum. They contain path'
            ' names which',
            '# match the buildroot and must be removed or the package will '
            'fail to build.',
            'find %{buildroot} -name "RECORD" -exec rm -rf {} \\;',
            '# Change the virtualenv path to the target installation '
            'direcotry.',
            '# venvctrl-relocate --source=%{venv_dir}'
            ' --destination=/%{venv_install_dir}',
        ))

        if config.python_centos_venv.strip_binaries:
            spec.blocks.install.extend((
                '# Strip native modules as they contain buildroot paths in'
                'their debug information',
                'find %{venv_dir}/lib -type f -name "*.so" | xargs -r strip',
            ))
        spec.blocks.install.extend((
            '# Remove symlink directories (lib64 -> lib)',
            'for link in `find %{venv_dir} -type l` ; do source=`readlink -f $link` ; unlink $link ; cp -r $source $link ; done',
            r'pathfix.py -pni "%{__python3} %{py3_shbang_opts}" %{buildroot}/%{venv_install_dir} `grep -lr "^#!/usr/bin/env python$" %{buildroot}/%{venv_install_dir} | grep "\.py" | egrep "\-[^/]+$"`',
        ))

        return spec

