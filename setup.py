from setuptools import setup, find_packages

setup(
    name="lmutual",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["pytest>=7", "jsonschema>=4"],
    python_requires=">=3.9",
)
