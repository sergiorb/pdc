from setuptools import setup, find_packages

setup(
  name = "pdc",
  version = "1.1.7",
  packages = find_packages(),
  install_requires = ['pyserial>=3.0.1'],
  package_data = {
    '': ['*.txt', '*.rst', '*.md',],
  },

  # metadata for upload to PyPI
  author = "Sergio Romero Barra",
  author_email = "s.romerobarra@gmail.com",
  description = "Python Device Communication.",
  license = "MIT",
  keywords = "arduino serial communication",
  url = "https://github.com/sergiorb/pdc",
  download_url = 'https://github.com/sergiorb/pdc/tarball/1.1.7'
)