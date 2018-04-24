from setuptools import setup

setup(
    name='DepyTG',
    version='3.6-r0',
    packages=['depytg'],
    url='https://github.com/Depaulicious/DepyTG',
    license='',
    author='Davide Depau',
    author_email='davide@depau.eu',
    description='The only Telegram bot library that does nothing',
    requires=["requests"],
    extras_require={
        'flask': ['Flask'],
        'upload_streaming': ['requests_toolbelt']
    }
)
