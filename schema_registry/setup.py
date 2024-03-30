from setuptools import (
    find_packages,
    setup,
)

FILE_NAME = "VERSION"


def get_version():
    with open(FILE_NAME) as file:
        return file.read()


def get_base_requirements():
    with open("requirements.txt") as file:
        return file.readlines()


def get_long_description():
    with open("README.md", encoding="utf-8") as file:
        return file.read()


setup(
    name="schema_registry",
    version=get_version(),
    package_data={"schema_registry": ["schemas/*.json", "models/*.json"]},
    description="...",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="",
    author="Evgeniy Slobodkin",
    author_email="eugene.slobodkin@gmail.com",
    packages=find_packages(),
    install_requires=get_base_requirements(),
    include_package_data=True,
    zip_safe=False,
)
