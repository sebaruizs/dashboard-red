import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables desde .env

credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')

# Filtros streamlit

hoy = datetime.now()
fecha = st.sidebar.date_input('Seleccionar mes', hoy)

# Define el alcance (scopes) de la API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Carga las credenciales
credentials = Credentials.from_service_account_file(
    credentials_path, scopes=SCOPES)

# Autoriza el cliente de gspread
client = gspread.authorize(credentials)

# Abre la hoja de cálculo por ID
spreadsheet_id = '1YeIyGfJO__oCEkhx0aET7J-lubqcKIwxgmg7Q7Y-404'  # Reemplaza con tu ID de hoja de cálculo
spreadsheet = client.open_by_key(spreadsheet_id)

# # Selecciona la hoja (worksheet) por nombre
# sheet = spreadsheet.worksheet('Resumen')

dfs = []
titles = []

# Obtiene todas las hojas de la hoja de cálculo
for sheet in spreadsheet.worksheets():
    title = sheet.title
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    dfs.append(df)
    titles.append(title)

# Nombro todas las hojas de calculo extraidas
resumen = dfs[0]
resumen = resumen[resumen['Nombre'] != ''] # Elimino las filas vacias

clientes = dfs[1]
clientes = clientes[clientes['Nombre'] != ''] # Elimino las filas vacias


autos = dfs[2]
autos = autos[autos['Auto'] != ''] # Elimino las filas vacias

pagos_clientes = dfs[3]
pagos_clientes = pagos_clientes[pagos_clientes['Cliente N°'] != ''] # Elimino las filas vacias


pagos_autos = dfs[4]
pagos_autos = pagos_autos[pagos_autos['Auto N°'] != ''] # Elimino las filas vacias


clientes['Fecha Documento'] = pd.to_datetime(clientes['Fecha Documento'])
pagos_clientes['Fecha pago'] = pd.to_datetime(pagos_clientes['Fecha pago'])
pagos_autos['Fecha pago'] = pd.to_datetime(pagos_autos['Fecha pago'])


# Formatear la fecha para mostrar solo mes y año
mes_y_anio = fecha.strftime("%m/%Y")

pagos_filtered = pagos_clientes.copy()
pagos_filtered['Fecha pago'] = pagos_clientes['Fecha pago'].dt.strftime('%m/%Y')
pagos_filtered = pagos_filtered[pagos_filtered['Fecha pago'] == mes_y_anio]
pagos_filtered.drop(columns=['Cliente N°', 'N°', 'Tipo Documento', 'Importe Pagado 2', 'Notas'], inplace=True)

pagos_filtered_grouped = pagos_filtered.groupby('Nombre').sum()
pagos_filtered_grouped.drop(columns=['Fecha pago'], inplace=True)
pagos_filtered_grouped['Importe pagado'] = pagos_filtered_grouped['Importe pagado'].astype(int)

total_mensual = pagos_filtered['Importe pagado'].sum()

pagos_autos_filtered = pagos_autos.copy()
pagos_autos_filtered['Fecha pago'] = pagos_autos['Fecha pago'].dt.strftime('%m/%Y')
pagos_autos_filtered = pagos_autos_filtered[pagos_autos_filtered['Fecha pago'] == mes_y_anio]
pagos_autos_filtered.drop(columns=['Auto N°', 'N°', 'Tipo Documento', 'Importe Pagado 2', 'Notas'], inplace=True)

pagos_autos_filtered_grouped = pagos_autos_filtered.groupby('Chapa').sum()
pagos_autos_filtered_grouped.drop(columns=['Fecha pago'], inplace=True)

total_mensual_autos = pagos_autos_filtered['Importe pagado'].sum()

resumen_filtered = resumen[["Nombre", "Importe Pagado", "Estado", "Dias a favor"]]

# Eliminar la fila donde el nombre es "Julia"
resumen_filtered = resumen_filtered[resumen_filtered['Nombre'] != 'Julia']
resumen_filtered['Importe Pagado'] = resumen_filtered['Importe Pagado'].astype(int)

resumen_autos = pd.merge(autos[['Chapa', 'Color']], pagos_autos_filtered_grouped, on='Chapa', how='left')


# Función para formatear los números
def format_number(x):
    return f'{x:,}'.replace(',', '.')

# Aplicar la función a la columna "Importe Pagado"
resumen_filtered['Importe Pagado'] = resumen_filtered['Importe Pagado'].apply(format_number)
resumen_autos['Importe pagado'] = resumen_autos['Importe pagado'].astype(int)
resumen_autos['Importe pagado'] = resumen_autos['Importe pagado'].apply(format_number)
resumen_filtered['Dias a favor'] = resumen_filtered['Dias a favor'].apply(format_number)

resumen_filtered.reset_index(drop=True, inplace=True)
resumen_autos.reset_index(drop=True, inplace=True)

#Imprimir para streamlit
st.title('Resumen del mes de ' + mes_y_anio)
st.subheader(f'Ingreso del mes: {int(total_mensual):,}'.replace(",", "."))
st.subheader(f'Egresos del mes: {int(total_mensual_autos):,}'.replace(",", "."))
st.write('Resumen Ingresos: ')
st.table(resumen_filtered)
st.write('Resumen Egresos: ')
st.table(resumen_autos)







