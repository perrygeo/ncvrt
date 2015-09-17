from setuptools import setup

setup(
    name="ncvrt",
    version='0.0.1',
    author="Matthew Perry",
    author_email="perrygeo@gmail.com",
    entry_points = {
        'console_scripts': [
            'ncvrt = ncvrt:ncvrt',
        ],
    }
)
