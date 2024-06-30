from setuptools import find_packages, setup

setup(
    name='pachca-client',
    version='0.1.0',
    description='pachca.com API client',
    url='https://github.com/k1nky/pachca-client',
    author='Andrey Shalashov',
    author_email='avshalashov@yandex.ru',
    license='Apache 2.0',
    keywords='pachca client',
    install_requires=['requests'],
    packages=find_packages(exclude=['tests*']),
)
