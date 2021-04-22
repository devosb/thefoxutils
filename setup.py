from setuptools import setup, find_packages
setup(
    name='thefoxUtils',
    version='21.4',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'tf = thefoxUtils.tf:main',
            'unidump = thefoxUtils.unidump:main',
            'unikey = thefoxUtils.unikey:main',
            'unidata = thefoxUtils.unidata:main',
        ]
    },
)
