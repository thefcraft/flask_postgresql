from setuptools import setup, find_packages
setup(
    name="flask-pgsql",
    version="0.0.1",
    author="ThefCraft",
    author_email="sisodiyalaksh@gmail.com",
    url="https://github.com/thefcraft/flask_postgresql",
    description="A PostgreSQL library for Flask inspired by Flask-SQLAlchemy. This library provides an easy-to-use interface for interacting with PostgreSQL databases in Flask applications.",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["psycopg2"]
)