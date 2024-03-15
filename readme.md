# Flask PostgreSQL Library

The Flask PostgreSQL library provides a convenient interface for integrating PostgreSQL databases into Flask applications. This library simplifies database interactions by offering an easy-to-use API similar to Flask-SQLAlchemy.

## Installation

You can install the Flask PostgreSQL library using pip:

```
pip install flask-pgsql --user
```

## Usage

### Initializing the Database Connection

To initialize the PostgreSQL connection, import the `PostgreSQL` class from `flask_postgresql` and provide the necessary connection parameters:

```python
import os
from flask_postgresql import PostgreSQL

# Retrieve database connection parameters from environment variables
hostname = os.getenv("db_hostname")
port = int(os.getenv("db_port"))
database = os.getenv("db_database")
username = os.getenv("db_username")
password = os.getenv("db_password")

# Initialize the PostgreSQL connection
db = PostgreSQL(hostname=hostname, port=port, database=database, username=username, password=password)
```

### Defining Models

Define your database models by subclassing `db.Model`. Here's an example of defining `BLOGS` and `USERS` models:

```python
class BLOGS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    data = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"{self.id}). Name : {self.user_id}, title: {self.title}, description: {self.description}, data: {self.data}"

class USERS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20), nullable=False)
    userDescription = db.Column(db.String(300), nullable=False)
    userPNG = db.Column(db.String(50), nullable=False)
    userFollowers = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"{self.id}). Name : {self.userName}, userDescription: {self.userDescription}, userPNG: {self.userPNG}, userFollowers: {self.userFollowers}"
```


### Creating Tables

Create database tables using the `create_all()` method:

```python
db.create_all()
# or you can recreate any special table
# USERS.create()
# BLOGS.create()
```

### Querying Data

You can query data using the `query` attribute of your models:

```python
users = USERS.query.all()
user = USERS.query.get(id=12)
```

### Adding Data

You can add data to the database using the `add()` method:

```python
new_user = USERS(username="example_user")
db.session.add(new_user)
db.session.commit()
```

### Deleting Data

You can delete data from the database using the `delete()` method:

```python
user_to_delete = USERS.query.get(id)
user_to_delete.delete()
db.session.commit()
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
