
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://postgres:Julissa2318@localhost:5433/agrobio_db")

df = pd.read_sql("SELECT cultivo, anio, produccion, rendimiento FROM cultivos", engine)

# Gráfico de barras - rendimiento por cultivo
df.plot(kind='bar', x='cultivo', y='rendimiento', title='Rendimiento por cultivo', color='green')
plt.tight_layout()
plt.show()

# Gráfico de línea - producción por año
df.plot(kind='line', x='anio', y='produccion', title='Producción por año', marker='o', color='blue')
plt.tight_layout()
plt.show()