#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='salmon',
    version='0.1.6-dev',
    description="A simple metric collector with alerts.",
    long_description=open('README.rst').read(),
    author="Peter Baumgarter",
    author_email='pete@lincolnloop.com',
    url='https://github.com/lincolnloop/salmon',
    license='LICENSE',
    install_requires=[
        'django==1.6',
        'djangorestframework==2.3.9',
        'South==0.8.3',
        'logan==0.5.5',
        'gunicorn>=0.17.2,<0.18.0',
        'whisper==0.9.10',
        'dj-static==0.0.5',
        'pytz',
    ],
    entry_points={
        'console_scripts': [
            'salmon = salmon.core.runner:main',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
