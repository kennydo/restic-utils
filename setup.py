from setuptools import find_packages
from setuptools import setup

setup(
    name='restic-utils',
    version='0.0.1',
    description="Various CLI utilities for Restic backups",
    url='https://github.com/kennydo/restic-utils',
    author='Kenny Do',
    author_email='chinesedewey@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
    ],
    packages=find_packages(exclude=['tests']),
    package_data={
    },
    entry_points={
        'console_scripts': [
            'assert-recent-snapshots=restic_utils.bin.assert_recent_snapshots:main',
        ],
    },
)
