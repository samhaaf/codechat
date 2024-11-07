from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read the requirements.txt file
with open(this_directory / 'requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='codechat',  # New package name
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='An AI assistant for coding assistance.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/codechat',  # Replace with your repository URL
    packages=find_packages(include=['codechat', 'codechat.*', 'core', 'core.*']),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'codechat=codechat.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)
