import pymysql

# Configure the MySQL connection
connection = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password = '****************', # Enter your MySQL password
    cursorclass = pymysql.cursors.DictCursor)

DB_NAME = 'chefhub'

TABLES = {}

TABLES['users'] = (
        "CREATE TABLE IF NOT EXISTS `users` ("
    "`id` int NOT NULL AUTO_INCREMENT, "
    "`username` char(30) NOT NULL, "
    "`hash` varchar(255) NOT NULL, "
    "PRIMARY KEY (`id`)"
    ")"
)

TABLES['favorites'] = (
        "CREATE TABLE IF NOT EXISTS `favorites` ("
    "`id` int NOT NULL AUTO_INCREMENT,"
    "`user_id` int NOT NULL,"
    "`recipe_id` int NOT NULL,"
    "`recipe_name` varchar(255) DEFAULT NULL,"
    "`recipe_img` varchar(255) DEFAULT NULL,"
    "PRIMARY KEY (`id`),"
    "KEY `user_id` (`user_id`),"
    "CONSTRAINT `favorites_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)"
    ")"
)

def create_database(cursor):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

def create_tables(cursor):
    for table_name, text in TABLES.items():
        cursor.execute(text)

def main():
    with connection.cursor() as cursor:
        create_database(cursor)
        create_tables(cursor)
    connection.close()

if __name__ == "__main__":
    main()