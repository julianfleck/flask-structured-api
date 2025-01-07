from setuptools import find_packages, setup

# Read requirements files


def read_requirements(filename):
    with open(f"requirements/{filename}") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


# Read requirements
requirements = read_requirements("base.txt")
dev_requirements = [
    req for req in read_requirements("dev.txt") if not req.startswith("-r")
]
docs_requirements = [
    req for req in read_requirements("docs.txt") if not req.startswith("-r")
]

# Read README and add system requirements notice


def get_long_description():
    with open("README.md") as f:
        description = f.read()

    # Add system requirements notice
    requirements_notice = """
## System Requirements

Before installing, ensure you have:
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher

For full installation instructions, visit our [documentation](https://github.com/julianfleck/flask-structured-api#readme).
"""
    return description + requirements_notice


setup(
    name="flask-structured-api",
    version="0.1.0",
    author="Julian Fleck",
    author_email="dev@julianfleck.net",
    description="A structured Flask API boilerplate with built-in AI capabilities",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/julianfleck/flask-structured-api",
    project_urls={
        "Documentation": "https://github.com/julianfleck/flask-structured-api#readme",
        "Bug Reports": "https://github.com/julianfleck/flask-structured-api/issues",
        "Source Code": "https://github.com/julianfleck/flask-structured-api",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    exclude_package_data={
        "": ["backups/*", "migrations/*"],
    },
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "docs": docs_requirements,
        "test": [
            "pytest>=8.0.0,<9.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "pytest-mock>=3.12.0,<4.0.0",
            "pytest-asyncio>=0.23.0,<1.0.0",
        ],
        "postgres": ["psycopg2-binary>=2.9.0"],  # Optional PostgreSQL driver
        "redis": ["redis>=5.0.0"],  # Optional Redis driver
    },
    entry_points={
        "flask.commands": [
            "tokens=flask_structured_api.core.cli.tokens:tokens_cli",
            "api-keys=flask_structured_api.core.cli.api_keys:api_keys_cli",
            "backup=flask_structured_api.core.cli.backup:backup_cli",
        ],
        "console_scripts": [
            "flask-structured-api=flask_structured_api.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: System Administrators",
    ],
)
