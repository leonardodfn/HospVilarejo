# -*- coding: utf-8 -*-

import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from datetime import datetime
import db_manager # Importa o nosso gestor de base de dados

# --- Inicialização do Dashboard ---
app = Dash(__name__, title="HospVilarejo Dashboard")

app.layout = html.Div(style={'backgroundColor': '#f0f2f5', 'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1(
        "HospVilarejo - Painel de Análise de Feedback",
        style={'textAlign': 'center', 'color': '#1c1e21', 'padding': '20px'}
    ),
    html.Div(id='live-update-time', style={'textAlign': 'center', 'color': '#606770'}),
    
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000, # Atualiza a cada 60 segundos
        n_intervals=0
    ),
    
    html.Div(className='row', style={'padding': '20px', 'display': 'flex', 'flexWrap': 'wrap'}, children=[
        html.Div(className='six columns', style={'width': '48%', 'margin': '1%'}, children=[
            dcc.Graph(id='sentiment-pie-chart')
        ]),
        html.Div(className='six columns', style={'width': '48%', 'margin': '1%'}, children=[
            dcc.Graph(id='request-category-bar-chart')
        ]),
    ]),
    
    html.Div(className='row', style={'padding': '20px'}, children=[
        dcc.Graph(id='requests-time-series-chart')
    ]),

    html.Div(className='row', style={'padding': '20px'}, children=[
        html.H3("Últimos Pedidos e Reclamações", style={'color': '#1c1e21'}),
        html.Div(id='actionable-feedbacks-table')
    ])
])

# --- Callback para Atualização em Tempo Real ---

@app.callback(
    [Output('sentiment-pie-chart', 'figure'),
     Output('request-category-bar-chart', 'figure'),
     Output('requests-time-series-chart', 'figure'),
     Output('actionable-feedbacks-table', 'children'),
     Output('live-update-time', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    df = db_manager.load_data_for_dashboard() # Usa a função do nosso gestor
    
    # Gráfico de Pizza: Distribuição de Sentimentos
    sentiment_counts = df['sentiment'].dropna().value_counts()
    pie_fig = px.pie(
        values=sentiment_counts.values, 
        names=sentiment_counts.index, 
        title='Distribuição Geral de Sentimentos',
        color_discrete_map={'Positivo': '#28a745', 'Neutro': '#6c757d', 'Negativo': '#dc3545'}
    )
    
    # Filtra apenas para reclamações e pedidos
    actionable_df = df[df['intention'] == 'Reclamacao/Pedido'].copy()
    
    # Gráfico de Barras: Contagem por categoria
    if not actionable_df.empty:
        category_counts = actionable_df['category'].dropna().value_counts().sort_values(ascending=True)
    else:
        category_counts = pd.Series()
        
    bar_fig = px.bar(
        x=category_counts.values, 
        y=category_counts.index, 
        orientation='h',
        title='Principais Categorias de Pedidos e Reclamações'
    )
    bar_fig.update_layout(yaxis_title="Categoria", xaxis_title="Número de Solicitações")
    
    # Gráfico de Linha: Pedidos/Reclamações ao longo do tempo
    if not actionable_df.empty:
        requests_over_time = actionable_df.set_index('timestamp').resample('D').size().reset_index(name='contagem')
    else:
        requests_over_time = pd.DataFrame({'timestamp': [], 'contagem': []})
        
    line_fig = px.line(
        requests_over_time, 
        x='timestamp', 
        y='contagem',
        title='Número de Pedidos e Reclamações por Dia',
        markers=True
    )
    line_fig.update_layout(xaxis_title="Data", yaxis_title="Número de Solicitações")
    
    # Tabela: Últimos 5 pedidos/reclamações
    latest_actionable = actionable_df.sort_values(by='timestamp', ascending=False).head(5)
    table = html.Table(
        [html.Tr([html.Th(col) for col in ['Quarto/Reserva', 'Categoria', 'Mensagem', 'Data']])] +
        [html.Tr([
            html.Td(row['guest_identifier']),
            html.Td(row['category']),
            html.Td(row['original_message']),
            html.Td(row['timestamp'].strftime('%Y-%m-%d %H:%M'))
        ]) for index, row in latest_actionable.iterrows()],
        style={'width': '100%', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'}
    )
    
    update_time = f"Última atualização: {datetime.now().strftime('%H:%M:%S')}"
    
    return pie_fig, bar_fig, line_fig, table, update_time


# --- Execução do Servidor ---
if __name__ == '__main__':
    app.run(debug=True)
