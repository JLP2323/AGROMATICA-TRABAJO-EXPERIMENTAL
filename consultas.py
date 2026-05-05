import psycopg2
import pandas as pd

conn = psycopg2.connect(
    dbname="agrobio_db",
    user="postgres",
    password="Julissa2318",
    host="localhost",
    port="5433"
)

# Producción total
cur = conn.cursor()
cur.execute("SELECT SUM(produccion) FROM cultivos")
print("Producción total:", cur.fetchone()[0])

# Número de cultivos
cur.execute("SELECT COUNT(*) FROM cultivos")
print("Total de cultivos registrados:", cur.fetchone()[0])

# Ver tabla como DataFrame
df = pd.read_sql("SELECT cultivo, anio, produccion, rendimiento FROM cultivos", conn)
print(df)

conn.close()