import os
from setuptools import setup

def readme(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ifttt",
    version = "0.0.8",
    author = "Brian Abelson",
    author_email = "brian@newslynx.org",
    description = "A Pythonic interface for building IFTTT plugins routed over email.",
    license = "MIT",
    keywords = "email, ifttt",
    url = "https://github.com/newslynx/ifttt",
    packages=['ifttt'],
    long_description=readme('README.md'),
    install_requires = ["pytz"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
    ],
)