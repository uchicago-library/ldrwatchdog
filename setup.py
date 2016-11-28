from setuptools import setup
from setuptools import find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()

setup(
    name = 'ldrwatchdog',
    description = "A suite of tools for performing watchdog functionality on digital repositories",
    long_description = readme(),
    version = '0.0.1dev',
    author = "Brian Balsamo, Tyler Danstrom",
    author_email = "balsamo@uchicago.edu, tdanstrom@uchicago.edu",
    keywords = [
        "uchicago",
        "repository",
        "file-level",
        "watchdog"
    ],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    dependency_links = [
        'https://github.com/uchicago-library/uchicagoldr-toolsuite' +
        '/tarball/master#egg=uchicagoldrtoolsuite',
        'https://github.com/uchicago-library/uchicagoldr-premiswork' +
        '/tarball/master#egg=pypremis',
    ],
    entry_points =  {'console_scripts': ['postarchive = ldrwatchdog.app.postarchiver:main',
                                         'fixitycheck = ldrwatchdog.app.fixitychecker:main',
                                         'updatecollections = ldrwatchdog.app.updatecollections:main']},
    scripts=["bin/postarchive_cron",
             "bin/fixitycheck_cron"]
)
