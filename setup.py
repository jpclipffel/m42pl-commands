from setuptools import setup, find_packages


setup(
  name='m42pl-commands',
  author='@jpclipffel',
  url='https://github.com/jpclipffel/m42pl-commands',
  version='1.0.0',
  packages=find_packages(),
  install_requires=[
    'm42pl',
    # ---
    'pyzmq>=22.3.0',
    'aiohttp>=3.8.1',
    'pygments>=2.10.0',
    'lxml>=4.7.1',
    'jsonpath-ng>=1.5.3',
    'jinja2>=3.0.3',
    'tabulate>=0.8.9',
    'types-tabulate>=0.8.3'
  ]
)
