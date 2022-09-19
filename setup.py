import os.path
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# # The text of the README file
# with open(os.path.join(HERE, "README.md")) as fid:
#     README = fid.read()

# This call to setup() does all the work
setup(
    name='f4obscontroller',
    version='1.0.0',
    description='',
    packages=['src'],
    include_package_data=True,
    install_requires=[
        'websockets' == '9.0.1', 'keyboard' == '0.13.5'
    ],
    entry_points={"console_scripts": ["f4obscontroller=src.main:main"]},
)
