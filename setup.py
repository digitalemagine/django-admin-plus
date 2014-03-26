# -*- coding: utf-8 -*-
#from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

exec(open('admin_plus/_version.py').read())

setup(
    name='django-admin-plus',
    version=__version__,
    author=u'Stefano Crosta',
    author_email='stefano@digitalemagine.com',
    packages=find_packages(),
    include_package_data=True,
#    install_requires = [
#    ],
#    url='http://github.org/digitalemagine/django-admin-plus',
    license='TBD',
    description='Adding some automagic to Django contrib.admin',
    long_description=open('README.md').read(),
    zip_safe=False,
)