from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))


setup(
    name="git_superlog",

    version="0.0",

    description="API and scripts for more advanced git logs",

    author="H. Onur Solmaz",

    packages=find_packages(exclude=["contrib", "docs", "tests"]),

    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },

    # package_data={
    #     "sample": ["package_data.dat"],
    # },

    # data_files=[("my_data")],

    install_requires={
    },

    entry_points={
        "console_scripts": [
            "git-superlog=git_superlog.main:__main__",
        ],
    },
)
