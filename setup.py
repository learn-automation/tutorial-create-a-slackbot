from setuptools import setup

version = '1.0.0'

requirements = [
    'requests',
    'slackclient'
]

dev_requirements = [
    'pytest'
]

setup(name='tutorial_bot',
      version=version,
      description="Lists tutorials in learn-automation's github",
      author='Jonny Carlyon',
      author_email='jonathoncarlyon@gmail.com',
      url='Link coming soon...',
      install_requires=requirements,
      extras_require={'dev': dev_requirements},
      packages=['bot'],
      )
