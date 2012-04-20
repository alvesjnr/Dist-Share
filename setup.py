"""
    DistShare - A distribution manager
"""

from setuptools import setup

setup(name='Dist Share',
      version='0.1',
      description='Distributions manager',
      author='Intec Photonics',
      author_email='intec@ugent.be',
      url='',
	    install_requires=['pygit'],
      packages=['dist_share'],
      entry_points = {
        'console_scripts': [
            'dist-share = dist_share.app:main',
        ],
      },
     )
