from setuptools import (
    find_packages,
    setup,
)


setup(
    name='restic-check',
    version='0.0.1',
    description="Check on your restic backups",
    url='https://github.com/kennydo/restic-check',
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
        ],
    },
)
