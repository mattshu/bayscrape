import setuptools

setuptools.setup(
    name='bayscrape',
    version='0.2',
    packages=setuptools.find_packages(),
    setup_requires=['flake8'],
    install_requires=[
        'requests>=2.24.0',
        'beautifulsoup4>=4.9.3',
        'colored>=1.4.2',
        'setuptools>=50.3.2',
        'beautifultable>=1.0.0',
    ],
    url='https://github.com/mattshu/bayscrape',
    license='GNU GPLv3',
    author='Matt Kelley',
    author_email='mattshu32@gmail.com',
    description='Safely browse legal torrents from the comfort of your command-line.'
)
