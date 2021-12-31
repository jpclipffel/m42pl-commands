from setuptools import setup


setup(
  name='m42pl-commands',
  author='@jpclipffel',
  url='https://github.com/jpclipffel/m42pl-commands',
  version='1.0.0',
  packages=['m42pl_commands',],
  install_requires=[
    # 'm42pl',
    # ---
    # 'msgpack>=1.0.3',
    # 'zmq',
    'pyzmq>=22.3.0',
    # 'redis>=4.0.2',
    # 'requests',
    'aiohttp>=3.8.1',
    'pygments>=2.10.0',
    'lxml>=4.7.1',
    'jsonpath-ng>=1.5.3',
    'jinja2>=3.0.3',
    'tabulate>=0.8.9',
    'types-tabulate>=0.8.3'
  ]
)
