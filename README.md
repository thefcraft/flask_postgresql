# Flask PostgreSQL Library

The Flask PostgreSQL library provides a convenient interface for integrating PostgreSQL databases into Flask applications. This library simplifies database interactions by offering an easy-to-use API similar to Flask-SQLAlchemy.

## Installation

DEMO: i made [mediumClone](https://github.com/thefcraft/mediumClone/) using both Flask-SQLAlchemy and flask_postgresql with change of two three line of code.
In this demo i use flask_login library which is also supported by my flask_postgresql library.

You can install the Flask PostgreSQL library using pip:

```
pip install flask-pgsql --user
```

## TODO
- add support flask_login library ✅
    ```python
    from flask_login import UserMixin, LoginManager, ...
    class USERS(UserMixin, db.Model): ...
    ```
- use metaclass because Class properties are deprecated in Python 3.11 and will not be supported in Python 3.13
    ```python
    class BaseModel:
    ...
    @classmethod
    @property # Class properties are deprecated in Python 3.11 and will not be supported in Python 3.13
    def query(cls): ...
    ```
    Do somethig like this.
  
    ```python
    class MetaModel(type): ...
    class BaseModel(metaclass=MetaModel): ...
    ```

## Usage

### Works on existing code

```python
from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database\\database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) # Creating an SQLAlchemy instance
...
if __name__ == "__main__":
    if RESET:
        with app.app_context(): db.create_all()
```
replace it by
```python
from flask_postgresql import PostgreSQL
db = PostgreSQL(hostname=hostname, port=port, database=database, username=username, password=password)
...
if __name__ == "__main__":
    if RESET:
        db.create_all() # with app.app_context(): db.create_all() will also work
```
### array support
```python
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Integer, array=True)

    def __repr__(self):
        return f"Test({self.id}, {self.data})"
db.create_all()
p = Test(data = [21, 24])
db.session.add(p)
db.session.commit()
Test.query.get(id=1).data #-> [21, 24]    
```

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
    data = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"{self.id}). Name : {self.user_id}, title: {self.title}, description: {self.description}, data: {self.data}"

class USERS(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    bio = db.Column(db.Text)
    details = db.Column(db.JSON, nullable=True)
    profile_image = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __repr__(self):
        return f"Test({self.id}, {self.username}, {self.email}, {self.age}, {self.is_active}, {self.bio}, {self.profile_image}, {self.created_at})"
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

### Compatibility 
While the Flask PostgreSQL library is designed for Flask applications, it can also be used in other frameworks or standalone Python scripts that require PostgreSQL database integration.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
