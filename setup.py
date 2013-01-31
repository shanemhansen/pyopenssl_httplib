#!/usr/bin/env python
"""
"""
from distutils.core import setup

setup(name='pyopenssl_httplib',
      version='1.0',
      description='httplib and urllib3 pyopenssl integration',
      author='Shane Hansen',
      author_email='shanemhansen@gmail.com',
      url='http://github.com/shanemhansen/pyopenssl_http',
      install_requires=['pyOpenSSL'],
      platforms='any',
      license='MIT',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules'
          'Programing Language :: Python'
      ],
      py_modules=['pyopenssl_httplib'])
