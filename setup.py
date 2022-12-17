import os
from distutils.command.build import build

from django.core import management
from setuptools import setup, find_packages
from pretix_reluctant_stripe import __version__


try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = ''


class CustomBuild(build):
    def run(self):
        management.call_command('compilemessages', verbosity=1)
        build.run(self)


cmdclass = {
    'build': CustomBuild
}


setup(
    name='pretix-reluctant-stripe',
    version=__version__,
    description='Short description',
    long_description=long_description,
    url='https://github.com/metarheinmain/pretix-reluctant-stripe',
    author='Team MRMCD',
    author_email='popcorn@mrmcd.net',
    license='Apache Software License',

    install_requires=[],
    packages=find_packages(exclude=['tests', 'tests.*']),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_reluctant_stripe=pretix_reluctant_stripe:PretixPluginMeta
""",
)
