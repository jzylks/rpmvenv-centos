rpmvenv-centos
==============

*CentOS extensions for RPM package helper which support packaging Python virtual environments.*

Basic Usage
-----------

In order to package a Python project in an RPM containing a virtualenv drop
a file in your repository root with a '.json' extensions and the following
content. Change the values where appropriate.

    {
        "extensions": {
            "enabled": [
                "python_centos_venv",
                ...
            ]
        },
        ...
        "python_centos_venv": {
            "name": "name_of_venv_dir_to_create",
            "path": "/path/where/to/install/venv"
        },
        ...
    }

Refer to the rpmvenv package for more detailed examples.
