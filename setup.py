import setuptools
import tinkerer

with open('README.md', 'r') as file:
    long_description = file.read()

with open('requirements.txt', 'r') as file:
    dependencies = file.read().split('\n')[:-1]

setuptools.setup(
    name=tinkerer.APP_NAME,
    version=tinkerer.APP_VERSION,
    author=tinkerer.APP_AUTHOR,
    license=tinkerer.APP_LICENSE,
    license_file='./LICENSE',
    description=tinkerer.APP_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=tinkerer.APP_URL,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console :: Curses",
        "Topic :: Games/Entertainment"
    ],
    install_requires=dependencies,
    python_requires='>=3.8.5',
)
