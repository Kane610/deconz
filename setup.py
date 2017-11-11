# https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/
# http://peterdowns.com/posts/first-time-with-pypi.html
# pip install /home/pi/pydeconz/ --target /home/pi/home-assistant/venv/lib/python3.4/site-packages/ --upgrade
# pip install -e /home/pi/pydeconz/
# Upload to PyPI Live
# python setup.py sdist upload -r pypi
# python setup.py sdist bdist_wheel upload
# python setup.py sdist bdist_wheel
# twine upload dist/*

from setuptools import setup

setup(
  name='pydeconz',
  packages=['pydeconz'],
  version='8',
  description='A python library for communicating with deconz REST-API from dresden elektronik',
  author='Robert Svensson',
  author_email='Kane610@users.noreply.github.com',
  license='MIT',
  url='https://github.com/Kane610/deconz',
  download_url='https://github.com/Kane610/deconz/archive/v8.tar.gz',
  install_requires=['aiohttp'],
  keywords=['deconz', 'zigbee', 'homeassistant'],
  classifiers=[
    'Natural Language :: English',
    'Programming Language :: Python :: 3',
  ],
)
