from setuptools import setup, find_packages

required_packages = ['graphql-core==0.5b3', 'django>=1.8.0']

setup(
    name='graphql-django-view',
    version='1.3b1',
    description='A django view that will execute a GraphQL Schema',
    url='https://github.com/graphql-python/graphql-django-view',
    download_url='https://github.com/graphql-python/graphql-django-view/releases',
    author='Syrus Akbary',
    author_email='me@syrusakbary.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
    ],

    keywords='api graphql protocol rest django',
    packages=find_packages(exclude=['tests']),
    install_requires=required_packages,
    tests_require=['pytest>=2.7.3'],
)
