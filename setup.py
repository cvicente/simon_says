# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

__version__ = None
exec(open("simon_says/version.py").read())

setup(
    name="simon_says",
    version=__version__,
    description="GE/Interlogix Simon XT Alarm interface library and API",
    long_description="Interact with the Simon XT Alarm system",
    author="Carlos Vicente",
    author_email="cvicente@gmail.com",
    url="https://github.com/cvicente/simon_says",
    license="GPL v3.0",
    classifiers=(
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ),
    packages=find_packages(exclude=["tests", "tests.*"]),
    # required for PEP-561 compatible typed packages.
    zip_safe=False,
    setup_requires=["setuptools", "pytest"],
    # pip install consults this list by specifying . in requirements.txt
    install_requires=[
        "configparser",
        "falcon",
        "gunicorn",
        "httpie",
        "pycall",
        "pydantic",
        "pyyaml",
        "redis",
        "requests",
    ],
    extras_require={
        "dev": ["mock", "pytest", "pytest-localserver", "pytest-mock", "tox"],
        "lint": ["black", "flake8", "isort"],
    },
    scripts=["bin/simon_event_handler", "bin/simon_event_handler"],
)
