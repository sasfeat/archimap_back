import os

webserver_host = 'localhost'
webserver_port = 5000

db_name = 'archimap'
db_port = 5432
db_host = 'localhost'
db_user = 'postgres'
db_pass = 'post@lex95'


if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = "postgresql://" \
                    + ":".join([db_user, db_pass]) \
                    + "@" + ":".join([db_host, str(db_port)]) \
                    + "/" + db_name
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']