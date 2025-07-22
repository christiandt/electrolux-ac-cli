from setuptools import setup, find_packages

setup(
    name="electrolux-cli",
    version="0.1.0",
    description="CLI for controlling Electrolux air conditioners",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "fire",
        "broadlink"
    ],
    entry_points={
        "console_scripts": [
            "electrolux=electrolux.cli:main"
        ]
    },
    python_requires=">=3.7",
)
