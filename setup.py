from setuptools import setup, find_packages

setup(
    name='flask_ai_api_boilerplate',
    version='0.1',
    packages=find_packages(include=['app', 'app.*']),
    install_requires=[
        'Flask',
        'flask-openapi3',
        'flask-migrate',
        'psycopg2-binary',
        'python-dotenv',
        'pydantic',
        'pydantic-settings',
        'supervisor',
    ],
    python_requires='>=3.11',
)
