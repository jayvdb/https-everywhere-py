#!/usr/bin/env python

from setuptools import find_packages, setup

classifiers = """\
Environment :: Console
Environment :: Plugins
Environment :: Web Environment
Intended Audience :: Developers
Intended Audience :: Science/Research
Intended Audience :: System Administrators
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: Implementation :: CPython
Topic :: Internet :: WWW/HTTP :: Browsers
Topic :: Internet :: WWW/HTTP :: Session
Topic :: Security
Development Status :: 4 - Beta
"""

setup(
    name="https-everywhere",
    version="0.2.0",
    description="Privacy for Pythons. Requests adapters for HTTPS, including HSTS preloading and HTTPS Everywhere rules",
    license="Apache-2.0",
    author_email="jayvdb@gmail.com",
    url="https://github.com/jayvdb/https-everywhere-py",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
    install_requires=[
        "requests[security]",
        "sre-yield",
        "appdirs",
        "logzero",
        "cached-property",
    ],
    classifiers=classifiers.splitlines(),
    tests_require=["unittest-expander", "lxml", "tldextract", "regex"],
    # lxml is optional, needed for testing upstream rules
)
