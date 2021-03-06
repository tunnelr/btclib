from setuptools import find_packages, setup  # type: ignore

import btclib

with open("README.md", "r") as fh:
    longdescription = fh.read()

setup(
    name=btclib.name,
    version=btclib.__version__,
    url="https://btclib.org",
    project_urls={
        "Download": "https://github.com/btclib-org/btclib/releases",
        "Documentation": "https://btclib.readthedocs.io/",
        "GitHub": "https://github.com/btclib-org/btclib",
        "Issues": "https://github.com/btclib-org/btclib/issues",
        "Pull Requests": "https://github.com/btclib-org/btclib/pulls",
    },
    license=btclib.__license__,
    author=btclib.__author__,
    author_email=btclib.__author_email__,
    description="A library for 'bitcoin cryptography'",
    long_description=longdescription,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={"btclib": ["data/*", "tests/test_data/*", "py.typed"]},
    test_suite="btclib.tests",
    keywords=(
        "bitcoin cryptography elliptic-curves ecdsa schnorr RFC-6979 "
        "bip32 bip39 electrum base58 bech32 segwit message-signing "
        "bip340"
    ),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
