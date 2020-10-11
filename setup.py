from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='LEMPA',
    version='0.4.2',
    packages=['states'],
    url='https://github.com/rbenamotz/LEMPA',
    license='',
    author='Roey Benamotz',
    author_email='roey@benamotz.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='RPi MCU Programmer'
)
