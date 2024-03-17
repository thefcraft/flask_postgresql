import psycopg2
from psycopg2 import sql
import json
class BaseType:
    def __init__(self, name):
        self.__name__ = name

# from flask import Flask, Response, render_template, send_from_directory, jsonify, request, redirect
class DBSession:
    def __init__(self, conn): self.conn = conn
    def add(self, p): 
        try:
            p.add(self.conn)
        except psycopg2.Error as e:
            # Rollback the transaction in case of an error
            self.conn.rollback()
            print("Error:", e)
    def commit(self): self.conn.commit()
    
class BaseList:
    def __init__(self, data:list) -> None:
        self.data = data
    def __len__(self): return len(self.data)
    def __getitem__(self, idx): return self.data[idx]
    def first(self): return self.data[0]
    
class Query:
    def __init__(self, cls, conn, attributes:list):
        self.table_name = cls.__name__
        self.cls = cls
        self.conn = conn
        self.attributes = attributes
    def all(self):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {self.table_name}")
        rows = cur.fetchall()
        cur.close()
        return [self.cls(**{
            atr:row[i].tobytes() if isinstance(row[i], memoryview) else row[i] for i,atr in enumerate(self.attributes)
        }) for row in rows]
    def get(self, id): 
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {self.table_name} WHERE id = {id}")
        row = cur.fetchone()
        cur.close()
        return self.cls(**{
            atr:row[i].tobytes() if isinstance(row[i], memoryview) else row[i] for i,atr in enumerate(self.attributes) # TODO 
        })
    # TODO
    def filter_by(self, **kwargs):
        cur = self.conn.cursor()
        cur.execute(f"""SELECT * FROM users WHERE {' and '.join([f"{k} = '{v}'" for k,v in kwargs.items()])};""")
        rows = cur.fetchall()
        cur.close()
        return BaseList([self.cls(**{
            atr:row[i].tobytes() if isinstance(row[i], memoryview) else row[i] for i,atr in enumerate(self.attributes)
        }) for row in rows])
    # def filter_by()
    # def order_by
    # def limit

class PostgreSQL:
    def __init__(selfRoot, hostname, port, database, username, password):
        connection_string = f"dbname={database} user={username} password={password} host={hostname} port={port}"
        # print(connection_string)
        selfRoot.conn = psycopg2.connect(connection_string)
        selfRoot.session = DBSession(selfRoot.conn)
        selfRoot.CURRENT_TIMESTAMP = 'CURRENT_TIMESTAMP'
        class BaseModel:
            def __init__(self, *args, **kwargs):
                # args not accepted yet
                assert args.__len__() == 0
                # assert self.id # required at this point
                for k, v in kwargs.items():
                    setattr(self, k, v)
                    # print(f"{k} : {getattr(self, k)}")
                self.kwargs = kwargs

            def add(self, conn):
                data = [i for i in self.kwargs.items()]
                head = ', '.join([str(i[0]) for i in data])
                value = [psycopg2.Binary(i[1]) if isinstance(i[1], bytes) else (json.dumps(i[1]) if isinstance(i[1], dict) else i[1]) for i in data]
                cur = conn.cursor()
                cur.execute(f"INSERT INTO {self.__class__.__name__} ({head})VALUES ({', '.join(['%s']*len(value))})", value)
                
                cur.close()
            def delete(self):
                try:
                    cur = selfRoot.conn.cursor()
                    cur.execute(f"DELETE FROM {self.__class__.__name__} WHERE id = {self.id}")
                    cur.close()
                except psycopg2.Error as e:
                    # Rollback the transaction in case of an error
                    selfRoot.conn.rollback()
                    print("Error:", e)
            
            @classmethod
            def create(cls):
                attributes = []
                for attr, value in vars(cls).items():
                    # Exclude magic methods and attributes starting with '__'
                    if not attr.startswith("__"):
                        attributes.append((attr, value))
                assert 'id' in [i[0] for i in attributes]
                # i[1][1] => false
                cur = selfRoot.conn.cursor()
                cur.execute(f'DROP TABLE IF EXISTS {cls.__name__};')
                call = ','.join(['id serial PRIMARY KEY']+[f"{i[0]} {i[1][0].replace('LargeBinary', 'bytea').replace('BigInteger', 'bigint').replace('DateTime', 'date').lower()}{' []' if i[1][5] else ''}{' UNIQUE' if (i[1][3]) else ''}{'' if (i[1][2] or i[1][4]!=None) else ' NOT NULL'}{'' if i[1][4]==None else ' DEFAULT '+str(i[1][4])}" for i in attributes if i[0]!='id'])
                cur.execute(f'CREATE TABLE {cls.__name__} ({call});')
                cur.close()
                
            @classmethod
            @property # Class properties are deprecated in Python 3.11 and will not be supported in Python 3.13
            def query(cls): 
                attributes = []
                for attr, value in vars(cls).items():
                    # Exclude magic methods and attributes starting with '__'
                    if not attr.startswith("__"):
                        attributes.append(attr)
                return Query(cls, selfRoot.conn, attributes)
        
        class BaseFunc:
            def now(): return selfRoot.CURRENT_TIMESTAMP
            
        selfRoot.Model = BaseModel
        selfRoot.func = BaseFunc
    # TODO Array support to flask_postgresql
    def Column(self, data_type, primary_key=False, nullable=True, unique=False, default=None, array=False):
        return (data_type.__name__,primary_key,nullable,unique,default, array)
    def Integer(self): ...
    def String(self, length:int=0): return BaseType(f'varchar({length})')
    def Text(self): ...
    def Boolean(self): ...
    def Numeric(self, a:int, b:int): return BaseType(f'numeric({a},{b})')
    def JSON(self): ...
    def BigInteger(self): ... # bigInt
    def BigInt(self): ...
    def LargeBinary(self): ...# // BYTEA
    def Bytea(self): ...
    # def Interval(self): ... TODO not implemented
    def Timestamp(self): ... 
    def DateTime(self): ...
    # db.Column(db.Enum('pending', 'processing', 'shipped', name='order_status'), nullable=False)
    # TODO
    # def Enum(self, *enum_values, name=None):
        # create_enum_query = sql.SQL("CREATE TYPE "+name+" AS ENUM ({})").format(sql.SQL(', ').join(map(sql.Literal, enum_values)))
        # cur.execute(create_enum_query)
    
    def create_all(self): 
        """
        Create all tables defined by model classes.
        """
        try:
            for cls in self.Model.__subclasses__():
                cls.create()
            self.session.commit()
        except psycopg2.Error as e:
            # Rollback the transaction in case of an error
            self.conn.rollback()
            print("Error:", e)
    


if __name__ == '__main__':
    # app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database\\database.db')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db = SQLAlchemy(app) # Creating an SQLAlchemy instance
    import os
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()

    hostname = os.getenv("db_hostname")
    port = int(os.getenv("db_port"))
    database = os.getenv("db_database")
    username = os.getenv("db_username")
    password = os.getenv("db_password")
    db = PostgreSQL(hostname=hostname, port=port, database=database, username=username, password=password)

    class BLOG(db.Model):
        # Id : Field which stores unique id for every row in 
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        title = db.Column(db.String(100), nullable=False)
        desc = db.Column(db.String(200), nullable=True)
        data = db.Column(db.Text, nullable=False)
        # date_added
        date = db.Column(db.DateTime, default=db.func.now())

        # repr method represents how one object of this datatable will look like
        def __repr__(self):
            return f"{self.id}). Name : {self.user_id}, title: {self.title}, desc: {self.desc}, data: {self.data}"

    class USER(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        userName = db.Column(db.String(20), nullable=False)
        userDescription = db.Column(db.String(300), nullable=False)
        userPNG = db.Column(db.String(50), nullable=False)
        userFollowers = db.Column(db.Integer, nullable=False)
        # userFollowers_id = 
        # repr method represents how one object of this datatable will look like
        def __repr__(self):
            return f"{self.id}). Name : {self.userName}, userDescription: {self.userDescription}, userPNG: {self.userPNG}, userFollowers: {self.userFollowers}"

    # p = USER(userName='laksh', userDescription='userDescription', userPNG='userPNG', userFollowers='userFollowers')
    # print(BLOG.create())
    print(BLOG.query.all())
    # db.session.add(p)
    # p.delete()
