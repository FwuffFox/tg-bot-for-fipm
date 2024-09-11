from setuptools import setup, find_packages

setup(
    name="tg-bot-fipm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={
        "console_scripts": [
            "tg-bot-fipm = src.main:main",
        ],
    },
)
