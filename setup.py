from setuptools import setup
setup(
    name='timestore',
    version='0.0.0',
    author='Guen Prawiroatmodjo',
    author_email='guenevere.p@gmail.com',
    packages=['timestore'],
    url='http://labfra.me',
    # license='LICENSE.txt',
    description='Package for storing time series in a PostgreSQL database.',
    long_description=open('README.md').read(),
    install_requires=[
        'pytest',
        'dataclasses',
        'psycopg2',
        'numpy',
        'pytz'
    ],
)
