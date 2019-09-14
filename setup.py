# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('Readme.md') as f:
    readme = f.read()

setup(
    name='btdripper',
    packages=find_packages(exclude=["tests", "docs"]),
    version='0.1.0-1',
    description='Control a Kamoer Dripping Pro pump',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Laurenz Altenmüller',
    author_email='pypi@laure.nz',
    url='https://github.com/lalten/btdripper',
    license='MIT',
    install_requires=['gatt', 'dbus-python'],
    scripts=['btdripper/btdripper.py']
)
