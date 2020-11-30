import setuptools
from setuptools import setup


with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

NAME = 'one-two-scrape'
VERSION = '0.0.2'
URL = 'https://github.com/SSripilaipong/otscrape'
LICENSE = 'MIT'
AUTHOR = 'SSripilaipong'
EMAIL = 'SHSnail@mail.com'

DESCRIPTION = ('A lightweight scraping module. Well-designed for readability and reusability. '
               'Compatible with popular data science frameworks.')

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Scientific/Engineering',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


setup(
    name=NAME,
    version=VERSION,
    packages=setuptools.find_packages(),
    url=URL,
    license=LICENSE,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    python_requires='>=3.6',
    install_requires=requirements,
    classifiers=CLASSIFIERS,
)
