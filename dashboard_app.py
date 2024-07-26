# Import packages
from dash import Dash, html, dash_table
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Load credentials from the JSON key file
credentials = Credentials.from_service_account_file(
    'fifth-octane-416622-95d9004d619a.json', scopes=SCOPES)

# Authorize the client
client = gspread.authorize(credentials)

# Open the Google Sheet by its ID
spreadsheet_id = '1YeIyGfJO__oCEkhx0aET7J-lubqcKIwxgmg7Q7Y-404'
spreadsheet = client.open_by_key(spreadsheet_id)

# Access a specific worksheet
worksheet = spreadsheet.get_worksheet(0)  # Get the first worksheet

# Get all records from the worksheet
data = worksheet.get_all_records()



dfs = []
titles = []

# Obtiene todas las hojas de la hoja de cálculo
for sheet in spreadsheet.worksheets():
    title = sheet.title
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    dfs.append(df)
    titles.append(title)
dfs
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

# Crear una fecha específica
fecha = pd.to_datetime('2024-07-01')

# Formatear la fecha para mostrar solo mes y año
mes_y_anio = fecha.strftime("%m/%Y")

clientes['Fecha Documento'] = pd.to_datetime(clientes['Fecha Documento'])
pagos_clientes['Fecha pago'] = pd.to_datetime(pagos_clientes['Fecha pago'])
pagos_autos['Fecha pago'] = pd.to_datetime(pagos_autos['Fecha pago'])

pagos_autos_filtered = pagos_autos.copy()
pagos_autos_filtered['Fecha pago'] = pagos_autos['Fecha pago'].dt.strftime('%m/%Y')
pagos_autos_filtered = pagos_autos_filtered[pagos_autos_filtered['Fecha pago'] == mes_y_anio]
pagos_autos_filtered.drop(columns=['Auto N°', 'N°', 'Tipo Documento', 'Importe Pagado 2', 'Notas'], inplace=True)

pagos_autos_filtered_grouped = pagos_autos_filtered.groupby('Chapa').sum()
pagos_autos_filtered_grouped.drop(columns=['Fecha pago'], inplace=True)

pagos_filtered = pagos_clientes.copy()
pagos_filtered['Fecha pago'] = pagos_clientes['Fecha pago'].dt.strftime('%m/%Y')
pagos_filtered = pagos_filtered[pagos_filtered['Fecha pago'] == mes_y_anio]
pagos_filtered.drop(columns=['Cliente N°', 'N°', 'Tipo Documento', 'Importe Pagado 2', 'Notas'], inplace=True)

pagos_filtered_grouped = pagos_filtered.groupby('Nombre').sum()
pagos_filtered_grouped.drop(columns=['Fecha pago'], inplace=True)

resumen_filtered = resumen[["Nombre", "Importe Pagado", "Estado", "Dias a favor"]]

# Eliminar la fila donde el nombre es "Julia"
resumen_filtered = resumen_filtered[resumen_filtered['Nombre'] != 'Julia']
resumen_filtered['Importe Pagado'] = resumen_filtered['Importe Pagado'].astype(int)

total_mensual = pagos_filtered['Importe pagado'].sum()

total_mensual_autos = pagos_autos_filtered['Importe pagado'].sum()

resumen_autos = pd.merge(autos[['Chapa', 'Color']], pagos_autos_filtered_grouped, on='Chapa', how='left')


# Inicializar la aplicación
app = Dash(__name__)

# Inicializar la aplicación
app = Dash(__name__)

# Layout de la aplicación
app.layout = html.Div([
    html.H1(f'Resumen del mes de {mes_y_anio}'),
    html.H2(f'Ingreso del mes: {total_mensual:,.0f}'),
    html.H2(f'Egresos del mes: {total_mensual_autos:,.0f}'),
    html.Div([
        html.H3('Resumen Ingresos:'),
        dash_table.DataTable(
            data=resumen_filtered.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in resumen_filtered.columns],
            page_size=10,
            style_cell={'textAlign': 'left'},
            style_table={'overflowX': 'auto'},
        )
    ], style={'padding': '10px', 'backgroundColor': '#f9f9f9'}),
    html.Div([
        html.H3('Resumen Egresos:'),
        dash_table.DataTable(
            data=resumen_autos.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in resumen_autos.columns],
            page_size=10,
            style_cell={'textAlign': 'left'},
            style_table={'overflowX': 'auto'},
        )
    ], style={'padding': '10px', 'backgroundColor': '#f9f9f9'}),
])

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)


