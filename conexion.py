import psycopg2

conn = psycopg2.connect(
    dbname="agrobio_db",
    user="postgres",
    password="Julissa2318",   # ←  cambia esto por tu contraseña real 
    host="localhost",
    port="5433"
)
print("Conexión exitosa")
conn.close()