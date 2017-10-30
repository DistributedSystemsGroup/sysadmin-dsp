from setuptools import setup

setup(
    name='pyostack',
    version='0.1',
    description='Simple OpenStack Python bindings',
    author='Daniele Venzano',
    author_email='venza@brownhat.org',
    packages=['pyostack'],
    test_suite='pyostack.tests',
    use_2to3=True,
    install_require=['python-novalicent', 'python-keystoneclient'],
)
