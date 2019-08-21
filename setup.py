# Imports from python.
import os
from setuptools import find_packages
from setuptools import setup


# Imports from geography.
from geography import __version__


REPO_URL = "https://github.com/The-Politico/politico-civic-geography/"

PYPI_VERSION = ".".join(str(v) for v in __version__)

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()


setup(
    name="politico-civic-geography",
    version=PYPI_VERSION,
    packages=find_packages(exclude=["docs", "tests", "example"]),
    include_package_data=True,
    license="MIT",
    description=(
        "Manage political geographic and spatial data, the POLITICO way."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    url=REPO_URL,
    author="POLITICO interactive news",
    author_email="interactives@politico.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords="",
    install_requires=[
        "boto3",
        "census",
        "DictObject",
        "django",
        "djangorestframework",
        "dj-database-url",
        "geojson",
        "psycopg2-binary",
        "politico-civic-utils",
        "pyshp",
        "shapely",
        "stringcase",
        "tqdm",
        "us",
    ],
    extras_require={
        "dev": ["sphinx", "sphinxcontrib-django", "sphinx-rtd-theme"],
        "test": ["pytest"],
    },
)
