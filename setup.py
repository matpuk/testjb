from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='librex',
    version='0.0.1',
    packages=['librex'],
    entry_points={
        'console_scripts': ['re-match = librex.main:cli']
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    url='https://github.com/matpuk/testjb',
    license='MIT',
    author='Grigory V. Kareev',
    author_email='grigory.kareev@gmail.com',
    description='Pure Python basic regular expressions implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
