import mysql.connector

try:
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="mediapp"
    )
    cursor = conexion.cursor()
    cursor.execute("DESCRIBE receta")
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    conexion.close()
except Exception as e:
    print(f"Error: {e}")
