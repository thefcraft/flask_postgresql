# Flask PostgreSQL Library

A PostgreSQL library for Flask inspired by Flask-SQLAlchemy. This library provides an easy-to-use interface for interacting with PostgreSQL databases in Flask applications.

## Installation

You can install the library using pip:

```
pip install flask-pgsql
```

## Usage

### Initializing the Database Connection

To initialize the database connection, create an instance of the `PostgreSQL` class:

```python
from flask_postgresql import PostgreSQL

db = PostgreSQL(hostname="your_host", port=your_port, database="your_database", username="your_username", password="your_password")
```

### Defining Models

Define your database models by subclassing `db.Model`:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    # Add more columns as needed

    def __repr__(self):
        return f"User(id={self.id}, username={self.username})"
```

### Creating Tables

Create database tables using the `create_all()` method:

```python
# db.create_all() # not working yet but you can use
User.create()
```

### Querying Data

You can query data using the `query` attribute of your models:

```python
users = User.query.all()
```

### Adding Data

You can add data to the database using the `add()` method:

```python
new_user = User(username="example_user")
db.session.add(new_user)
db.session.commit()
```

### Deleting Data

You can delete data from the database using the `delete()` method:

```python
user_to_delete = User.query.get(id)
user_to_delete.delete()
db.session.commit()
```

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
