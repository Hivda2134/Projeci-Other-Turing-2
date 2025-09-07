from setuptools import setup, find_packages

setup(
    name='projeci_other_turing',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pytest',
        'jsonschema',
    ],
    python_requires='>=3.8',
)


