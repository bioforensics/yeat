import pathlib
from setuptools import setup, find_packages
import versioneer


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='yeat',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='YEAT: Your Everday Assembly Tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bioforensics/yeat',
    packages=[
        "yeat",
        "yeat.tests",
    ],
    package_data={'yeat': ['yeat/data/*'],},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'yeat=yeat.cli:main',
        ],
    },
    classifiers=[
        "Environment :: Console",
        "Framework :: IPython",
        "Framework :: Jupyter",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Legal Industry",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    zip_safe=True,
    keywords='genome assembly',
    python_requires='>=3.7',
    project_urls={
        'Bug Reports': 'https://github.com/bioforensics/yeat/issues',
        'Source': 'https://github.com/bioforensics/yeat',
    },
)