import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    db="go"
)
print("connect ok")

cursor = conn.cursor()

def check(Login,Password):
    cursor.execute("select * from users where login =%s and password = %s",(Login,Password))
    user_data = cursor.fetchone()
    return user_data