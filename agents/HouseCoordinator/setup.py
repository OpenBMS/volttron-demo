from setuptools import setup, find_packages

packages = find_packages('.')
package = packages[0]

setup(
    name = package + '-openbms-agent',
    version = "0.1",
    install_requires = ['volttron', 'requests', 'pint'],
    packages = packages,
    entry_points = {
        'setuptools.installation': [
            'eggsecutable = ' + package + '.agent:main',
        ]
    }
)
