import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    db="go"
)

cursor = conn.cursor()

def check(Login, Password):
    cursor.execute("SELECT * FROM users WHERE login=%s AND password=%s", (Login, Password))
    user_data = cursor.fetchone()
    return user_data

def get_all_product():
    cursor.execute("""
        SELECT id_product, article, name, description, price, category, manufacturer
        FROM products
    """)
    return cursor.fetchall()