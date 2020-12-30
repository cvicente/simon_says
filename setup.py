# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name="simon_says",
    description="GE/Interlogix Simon XT Alarm interface library and API",
    long_description="Interact with the Simon XT Alarm system",
    author="Carlos Vicente",
    author_email="cvicente@gmail.com",
    url="https://github.com/cvicente/simon_says",
    license="GPL",
    classifiers=(
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
    ),
    packages=find_packages(exclude=["tests", "tests.*"]),
    # required for PEP-561 compatible typed packages.
    zip_safe=False,
    setup_requires=["setuptools", "pytest"],
    # pip install consults this list by specifying . in requirements.txt
    install_requires=[
        "configparser",
        "pycall",
        "pydantic",
        "pyyaml",
    ],
    extras_require={
        "dev": ["mock", "pytest", "pytest-mock", "tox", "tox-pyenv"],
        "lint": ["black", "flake8", "isort"],
    },
)
