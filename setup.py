from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='LEMPA',
    version='1.0',
    packages=['states'],
    url='',
    license='',
    author='Roey Benamotz',
    author_email='roey@benamotz.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='LEan Mean Programming mAchine'
)
