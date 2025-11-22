import pymysql
from config import Config

def create_database_if_not_exists():
    db_name = Config.get_db_name()

    # Extract host, user, password from DATABASE_URI
    uri = Config.SQLALCHEMY_DATABASE_URI.replace("mysql+pymysql://", "")
    credentials, host_and_db = uri.split("@")
    user, password = credentials.split(":")
    host = host_and_db.split("/")[0]

    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )

    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
    connection.commit()
    connection.close()
