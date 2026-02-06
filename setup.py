"""Setup script for epicsdev_tektronix package."""
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='epicsdev_tektronix',
    version='0.1.0',
    description='EPICS PVAccess device support for Tektronix oscilloscopes',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='ASukhanov',
    url='https://github.com/ASukhanov/epicsdev_tektronix',
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='EPICS PVAccess oscilloscope Tektronix MSO',
    entry_points={
        'console_scripts': [
            'epicsdev-tektronix=epicsdev_tektronix.tektronix_mso:main',
        ],
    },
)
