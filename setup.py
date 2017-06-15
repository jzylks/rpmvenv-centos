"""Setuptools configuration for rpmvenv-centos."""

from setuptools import setup
from setuptools import find_packages


setup(
    name='rpmvenv-centos',
    version='0.1.0',
    url='',
    description='CentOS extensions for RPM packager for Python virtualenv.',
    author="Jason Zylks",
    author_email="jzylks@tamu.edu",
    license='MIT',
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs']),
    install_requires=['rpmvenv'],
    entry_points={
        'rpmvenv.extensions': [
            'python_centos_venv = rpmvenv_centos.extensions.centos_venv:Extension',
        ]
    },
)
