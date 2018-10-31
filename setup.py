import sys
from setuptools import find_packages, setup

def install_deps():
    """Reads requirements.txt and preprocess it
    to be feed into setuptools.

    This is the only possible way (we found)
    how requirements.txt can be reused in setup.py
    using dependencies from private github repositories.

    Links must be appendend by `-{StringWithAtLeastOneNumber}`
    or something like that, so e.g. `-9231` works as well as
    `1.1.0`. This is ignored by the setuptools, but has to be there.

    Warnings:
        to make pip respect the links, you have to use
        `--process-dependency-links` switch. So e.g.:
        `pip install --process-dependency-links {git-url}`

    Returns:
         list of packages and dependency links.
    """
    default = open('requirements.txt', 'r').readlines()
    new_pkgs = []
    links = []
    for resource in default:
        """
        Do not install multiprocessing for Python 2.6+ or 3+:
        """
        py3_26_or_higher = sys.version_info[0]==3 or \
           (sys.version_info[0]==2 and sys.version_info[0]>5)
        if py3_26_or_higher and 'multiprocessing' in resource:
            pass
        elif 'git+https' in resource:
            pkg = resource.split('#')[-1]
            links.append(resource.strip() + '-9876543210')
            new_pkgs.append(pkg.replace('egg=', '').rstrip())
        else:
            new_pkgs.append(resource.strip())
    return new_pkgs, links


dependencies, dependency_links = install_deps()

setup(
    name='mtaac-package',
    version='0.0.1',
    url='https://github.com/cdli-gh/mtaac-package',
    license='BSD',
    author='Ilya Khait',
    author_email='ekh.itd@gmail.com',
    description='Reusable Python functions for MTAAC.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    package_data = {
        'data': ['*'],
        'mtaac_package': ['*'],
    },
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    dependency_links=dependency_links,
##    entry_points={
##        'console_scripts': [
##            'atf2conll = atf2conll_convertor.cli:main',
##        ],
##    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
