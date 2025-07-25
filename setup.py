from setuptools import setup, find_packages

setup(
    name="electrolux-cli",
    version="0.1.1",
    description="CLI for controlling Electrolux air conditioners",
    author="Christian Dancke Tuen",
    packages=find_packages(),
    install_requires=[
        "fire",
        "broadlink"
    ],
    entry_points={
        "console_scripts": [
            "elux=electrolux.cli:main"
        ]
    },
    python_requires=">=3.7",
)
