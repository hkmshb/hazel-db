from setuptools import setup, find_packages
import os.path as fs


HERE = fs.abspath(fs.dirname(__file__))
def readfile(name):
    with open(fs.join(HERE, name)) as f:
        return f.read()


requires = [
    'sqlalchemy',
    'zope.sqlalchemy'
]

tests_require = [
    'pytest',
    'pytest-cov'
]


setup(
    name='hazel-db',
    version='0.1.1',
    description='A library which eases integrating SQLAlchemy into a project',
    long_description='\n\n'.join([
        readfile('CHANGES.md'),
        readfile('README.md'),
    ]),
    author='Hazeltek Solutions',
    author_email='s.abdulhakeem@hotmail.com',
    url='https://bitbucket.org/hazeltek-dev/hazel-db',
    packages=find_packages(where='src', exclude=['tests']),
    package_dir={'': 'src'},
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=requires,
    extras_require={
        'testing': tests_require,
    },
    test_suite='tests',
    zip_safe=False,
    keywords='hazel sqlalchemy database db',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ]
)