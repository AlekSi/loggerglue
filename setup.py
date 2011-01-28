import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

execfile('loggerglue/version.py')

setup(name='loggerglue',
      version=__version__,
      description='Syslog protocol (rfc5424 and rfc5425) utilities',
      long_description= README + '\n\n' + CHANGES,
      author='Evax Software',
      author_email='contact@evax.fr',
      url='http://www.evax.fr/',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'setuptools',
          'pyparsing',
          ],
      keywords = ['syslog', 'rfc5424', 'rfc5425', 'TLS'],
      classifiers = [
              "Development Status :: 4 - Beta",
              "Intended Audience :: Developers",
              "Intended Audience :: System Administrators",
              "License :: OSI Approved :: MIT License",
              "Programming Language :: Python",
              "Operating System :: OS Independent",
              "Topic :: System :: Logging",
              "Topic :: Internet :: Log Analysis",
              ],
      test_suite = "loggerglue.tests",
      )

