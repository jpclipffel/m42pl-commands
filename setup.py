from setuptools import setup


setup(
  name='m42pl-commands',
  author='@jpclipffel',
  url='https://github.com/jpclipffel/m42pl-commands',
  version='1.0.0',
  packages=['m42pl_commands',],
  install_requires=[
    'm42pl',
    # ---
    'msgpack',
    'zmq',
    'redis',
    'requests',
    'aiohttp',
    'pygments',
    'lxml',
    'jsonpath-ng'
  ]
)
