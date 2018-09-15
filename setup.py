#!/usr/bin/env python3

# Copyright Dansk Bibliotekscenter a/s. Licensed under GPLv3
# See license text in LICENSE.txt or at https://opensource.dbc.dk/licenses/gpl-3.0/

from setuptools import setup, find_packages

setup(name="artifactory-utils",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description="",
    provides=["artifactory_utils"],
    entry_points=
        {"console_scripts": [
            "tags-from-templates = artifactory_utils.tags_from_templates:main",
            "docker-tags-lister = artifactory_utils.docker_tags_lister:main",
            "remote-tag = artifactory_utils.remote_tag:main"
        ]},
    install_requires=["requests==2.19.1"]
    )
