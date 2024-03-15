import psycopg2
class BaseType:
    def __init__(self, name):
        self.__name__ = name

# from flask import Flask, Response, render_template, send_from_directory, jsonify, request, redirect
class DBSession:
    def __init__(self, conn): self.conn = conn
    def add(self, p): p.add(self.conn)
    def commit(self): self.conn.commit()
    
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
            atr:row[i] for i,atr in enumerate(self.attributes)
        }) for row in rows]
    def get(self, id): 
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {self.table_name} WHERE id = {id}")
        row = cur.fetchone()
        cur.close()
        return self.cls(**{
            atr:row[i] for i,atr in enumerate(self.attributes)
        })

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
                value = [i[1] for i in data]
                cur = conn.cursor()
                cur.execute(f"INSERT INTO {self.__class__.__name__} ({head})VALUES ({', '.join(['%s']*len(value))})", value)
                
                cur.close()
            def delete(self):
                cur = selfRoot.conn.cursor()
                cur.execute(f"DELETE FROM {self.__class__.__name__} WHERE id = {self.id}")
                cur.close()
            
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
                call = ','.join(['id serial PRIMARY KEY']+[f"{i[0]} {i[1][0].replace('String', 'text').replace('string', 'varchar ').lower()}{'' if (i[1][2] or i[1][4]!=None) else ' NOT NULL'}{'' if i[1][4]==None else ' DEFAULT '+str(i[1][4])}" for i in attributes if i[0]!='id'])
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
        
        selfRoot.Model = BaseModel
    
    def Column(self, data_type, primary_key=False, nullable=False, unique=False, default=None):
        assert unique==False
        assert unique==False
        return (data_type.__name__,primary_key,nullable,unique,default)
    def Integer(self): ...
    def String(self, length:int=0): return BaseType(f'string({length})')
    def Date(self): ...
    def create_all(self): 
        """
        Create all tables defined by model classes.
        """
        for cls in self.Model.__subclasses__():
            cls.create()
        self.session.commit()

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
        data = db.Column(db.String, nullable=False)
        # date_added
        date = db.Column(db.Date, default=db.CURRENT_TIMESTAMP)

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
