from os import path

from setuptools import setup


here = path.abspath(path.dirname(__file__))

version_loc = path.join(here, "contextional", "__version__.py")
about = {}
with open(version_loc, "r") as f:
    exec(f.read(), about)


setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    url=about["__url__"],
    download_url=(
        "https://github.com/SalmonMode/contextional/archive/{}.tar.gz"
        .format(about["__version__"])
    ),
    author=about["__author__"],
    author_email=about["__author_email__"],

    license=about["__license__"],

    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],

    keywords=(
        "testing test-automation functional-testing testing-tools test tests "
        "development organization"
    ),
    packages=["contextional"],
    install_requires=[
        "pytest",
    ],
    test_suite="contextional.tests",
    entry_points={
        "nose.plugins.0.10": [
            "contextional-nose-dry-run = contextional.nose_plugin:NoseDryRun",
            ],
        },
)
