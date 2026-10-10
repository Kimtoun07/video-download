"""GrabVid — Universal Video Downloader."""
from setuptools import setup, find_packages

setup(
    name="grabvid",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2024.0",
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "grabvid=src.cli.main:main",
        ],
    },
    python_requires=">=3.8",
)
