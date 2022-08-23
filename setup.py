"""Setup for pydeCONZ."""

from setuptools import find_packages, setup

MIN_PY_VERSION = "3.9"
PACKAGES = find_packages(exclude=["tests", "tests.*"])
VERSION = "104"

setup(
    name="pydeconz",
    packages=PACKAGES,
    package_data={"pydeconz": ["py.typed"]},
    version=VERSION,
    description="A Python library for communicating with deCONZ REST-API from Dresden Elektronik",
    author="Robert Svensson",
    author_email="Kane610@users.noreply.github.com",
    license="MIT",
    url="https://github.com/Kane610/deconz",
    download_url=f"https://github.com/Kane610/deconz/archive/v{VERSION}.tar.gz",
    install_requires=["aiohttp", "async_timeout", "orjson"],
    tests_require=["aioresponses", "pytest", "pytest-aiohttp", "types-orjson"],
    keywords=["deconz", "zigbee", "homeassistant"],
    classifiers=["Natural Language :: English", "Programming Language :: Python :: 3"],
    python_requires=f">={MIN_PY_VERSION}",
)
