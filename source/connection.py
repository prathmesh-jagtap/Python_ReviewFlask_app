import mysql.connector as conn
from logger import log


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = conn.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        log.info("MySQL Database connection successful")
    except Exception as err:
        print(f"Error: '{err}'")

    return connection


my_database = create_server_connection('localhost', 'root', 'SQL123')

cursor = my_database.cursor()
# database created
# cursor.execute("CREATE SCHEMA product_reviews")

# cursor.execute("Show databases")
#
# for x in cursor:
#   print(x)
