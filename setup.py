#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='salmon',
    version='0.1.1',
    description="A monitoring system built on top of Salt.",
    long_description=open('README.rst').read(),
    author="Lincoln Loop",
    author_email='info@lincolnloop.com',
    url='https://github.com/lincolnloop/salmon',
    license='LICENSE',
    install_requires=[
        'django==1.5.1',
        'south==0.7.6',
        'pyyaml==3.10',
        'logan==0.5.5',
        'gunicorn>=0.17.2,<0.18.0',
    ],
    entry_points={
        'console_scripts': [
            'salmon = salmon.core.runner:main',
        ],
    },
    packages=find_packages(),
    package_data={'salmon': ['static/*.*', 'templates/*.*']},
)
