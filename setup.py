from setuptools import setup

setup(
    name='DepyTG',
    version='3.6-r0',
    packages=['depytg'],
    url='https://github.com/Depaulicious/DepyTG',
    author='Davide Depau',
    author_email='davide@depau.eu',
    description='The only Telegram bot library that does nothing',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: Chat',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    requires=["requests"],
    extras_require={
        'flask': ['Flask'],
        'upload_streaming': ['requests_toolbelt']
    }
)
