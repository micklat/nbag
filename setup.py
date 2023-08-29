#!/usr/bin/env python

from distutils.core import setup

setup(name='nbag',
      version='0.1',
      description='Infer the names of nodes in a computational graph from the LHS of ordinary assignment statements, by magic.',
      author='Michael Latowicki',
      url='https://github.com/micklat/nbag',
      packages=['nbag'],
      license='BSD 3-clause',
      install_requires=[
                      ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
      ],
)
