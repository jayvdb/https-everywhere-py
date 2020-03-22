#!/usr/bin/env python
"""HTTPS Everywhere."""

"""
Copyright 2020 John Vandenberg

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from setuptools import find_packages, setup

__version__ = "0.2.2"

classifiers = """\
Environment :: Console
Environment :: Plugins
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: Science/Research
Intended Audience :: System Administrators
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: Implementation :: CPython
Topic :: Internet :: WWW/HTTP :: Browsers
Topic :: Internet :: WWW/HTTP :: Session
Topic :: Security
Development Status :: 4 - Beta
"""

setup(
    name="https-everywhere",
    version=__version__,
    description="Privacy for Pythons. Requests adapters for HTTPS, including HSTS preloading and HTTPS Everywhere rules",
    license="Apache-2.0",
    author_email="jayvdb@gmail.com",
    url="https://github.com/jayvdb/https-everywhere-py",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
    install_requires=[
        "requests[security]",
        "appdirs",
        "logging-helper",
        "cached-property",
    ],
    classifiers=classifiers.splitlines(),
    tests_require=["unittest-expander", "lxml", "tldextract", "regex"],
    # lxml is optional, needed for testing upstream rules
)
