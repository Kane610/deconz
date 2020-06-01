"""Setup for deCONZ"""

# https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# http://peterdowns.com/posts/first-time-with-pypi.html
# pip install -e .
# Upload to PyPI Live
# python setup.py sdist bdist_wheel
# twine upload dist/pydeconz-* --skip-existing

from setuptools import setup

setup(
    name="pydeconz",
    packages=["pydeconz"],
    version="71",
    description="A Python library for communicating with deCONZ REST-API from Dresden Elektronik",
    author="Robert Svensson",
    author_email="Kane610@users.noreply.github.com",
    license="MIT",
    url="https://github.com/Kane610/deconz",
    download_url="https://github.com/Kane610/deconz/archive/v71.tar.gz",
    install_requires=["aiohttp"],
    keywords=["deconz", "zigbee", "homeassistant"],
    classifiers=["Natural Language :: English", "Programming Language :: Python :: 3"],
    python_requires=">=3.7.0",
)
