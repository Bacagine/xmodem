from setuptools import setup

setup(
    name='my_xmodem',
    version='0.1',
    description='A implementations of xmodem in python',
    author='Gustavo Bacagine',
    author_email='gustavo.bacagine@protonmail.com',
    packages=['my_xmodem'],  #same as name
    install_requires=['serial'], #external packages as dependencies
)

