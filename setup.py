from setuptools import find_packages, setup

setup(
    name='django-politico-civic-geography',
    version='0.0.0-alpha',
    description='',
    url='https://github.com/The-Politico/django-politico-civic-geography',
    author='POLITICO interactive news',
    author_email='interactives@politico.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords='',

    packages=find_packages(exclude=['docs', 'tests']),

    install_requires=[],

    extras_require={
        'test': ['pytest'],
    },
)
