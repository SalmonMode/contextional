from setuptools import setup, find_packages


__VERSION__ = "1.0.0"

setup(
    name="contextional",
    version=__VERSION__,
    description="A functional testing tool for Python",
    url="https://github.com/SalmonMode/contextional",
    download_url=(
        "https://github.com/SalmonMode/contextional/archive/{}.tar.gz"
        .format(__VERSION__)
    ),
    author="Chris NeJame",
    author_email="cnejame@truveris.com",

    license="MIT",

    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.6",
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
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=[
    ],
)
