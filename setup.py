from distutils.core import setup

from setuptools import find_packages

import alive_progress


def get_readme():
    with open('README.md', encoding='utf-8') as readme_file:
        return readme_file.read()


setup(
    name='alive-progress',
    version=alive_progress.__version__,
    description=alive_progress.__description__,
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/rsalmei/alive-progress',
    author=alive_progress.__author__,
    author_email=alive_progress.__email__,
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Natural Language :: English',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='progress bar progress-bar progressbar spinner eta monitoring python terminal '
             'multi-threaded REPL alive animated visual feedback simple live efficient monitor '
             'stats elapsed time throughput'.split(),
    packages=find_packages(exclude=['tests*']),
    data_files=[('', ['LICENSE'])],
    python_requires='>=3.9, <4',
    install_requires=['about_time==4.2.1', 'grapheme==0.6.0'],
)
