from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='thefoxUtils',
    version='21.5.0',
    author='Bobby de Vos',
    author_email='bobby_devos@sil.org',
    description='Unicode utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/devosb/thefoxutils',
    project_urls={
        'Bug Tracker': 'https://github.com/devosb/thefoxutils/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'tf = thefoxUtils.tf:main',
            'unidump = thefoxUtils.unidump:main',
            'unikey = thefoxUtils.unikey:main',
            'unidata = thefoxUtils.unidata:main',
        ]
    },
)
