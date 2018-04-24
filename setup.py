from setuptools import setup

setup(
    name='DepyTG',
    version='0.1',
    packages=['depytg'],
    url='https://github.com/Depaulicious/DepyTG',
    license='',
    author='Davide Depau',
    author_email='davide@depau.eu',
    description='The only Telegram bot library that does nothing',
    requires=["requests"],
    extras_require={
        'webhook_flask': ['Flask']
    }
)
