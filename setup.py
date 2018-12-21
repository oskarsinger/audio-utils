from distutils.core import setup
from setuptools import find_packages

export_packages = find_packages(where='.', include=('audioutils', 'audioutils.*'))

setup(
    name='audioutils',
    version='0.01',
    packages=export_packages
)
