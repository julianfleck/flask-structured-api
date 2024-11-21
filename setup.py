from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='flask-structured-api',
    version='0.1.0',
    author='Julian Fleck',
    author_email='dev@julianfleck.net',
    description='A structured Flask API boilerplate with built-in AI capabilities',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/julianfleck/flask-structured-api',
    project_urls={
        'Documentation': 'https://github.com/julianfleck/flask-structured-api#readme',
        'Bug Reports': 'https://github.com/julianfleck/flask-structured-api/issues',
        'Source Code': 'https://github.com/julianfleck/flask-structured-api',
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Flask',
    ],
    install_requires=[
        # Read from requirements/base.txt
        'Flask>=3.1.0,<4.0.0',
        'flask-openapi3>=4.0.2,<5.0.0',
        'flask-sqlalchemy>=3.1.1,<4.0.0',
        # ... rest of base requirements
    ],
    extras_require={
        'dev': [
            'debugpy>=1.8.8,<2.0.0',
            'black>=24.1.1,<25.0.0',
            'isort>=5.13.2,<6.0.0',
            'flake8>=7.0.0,<8.0.0',
            'mypy>=1.8.0,<2.0.0',
            'pre-commit>=3.6.0,<4.0.0',
        ],
        'test': [
            'pytest>=8.0.0,<9.0.0',
            'pytest-cov>=4.1.0,<5.0.0',
            'pytest-mock>=3.12.0,<4.0.0',
            'pytest-asyncio>=0.23.0,<1.0.0',
        ],
        'docs': [
            'mkdocs>=1.5.0,<2.0.0',
            'mkdocs-material>=9.5.0,<10.0.0',
            'mkdocstrings>=0.24.0,<1.0.0',
        ]
    },
    python_requires='>=3.10',
    entry_points={
        # Keep your existing entry points
    },
)
