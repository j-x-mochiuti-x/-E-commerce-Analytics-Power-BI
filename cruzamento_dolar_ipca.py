import pandas as pd
import os

# 1. Carregar os dados
df_vendas = pd.read_csv('data_processada/olist_master_data.csv', parse_dates=['order_purchase_timestamp'])
df_dolar = pd.read_csv('data/cotacao_dolar.csv', sep=';', encoding='latin1', skipfooter=10, engine='python') 
df_ipca = pd.read_csv('data/valor_ipca.csv', sep=',', encoding='latin1') 

print("🔄 Processando indicadores econômicos...")

# 2. Limpeza e Tipagem - DÓLAR
# Ajustando a data e convertendo a cotação para número
df_dolar['Data'] = pd.to_datetime(df_dolar['Data'], dayfirst=True)
df_dolar['cotacao_dolar'] = df_dolar['1 - u.m.c./US$'].str.replace(',', '.').astype(float)

# 3. Limpeza e Tipagem - IPCA (Inflação)
df_ipca = df_ipca[['Ano', 'Inflacaoo efetiva (Variacao do IPCA %)']].copy()
df_ipca.columns = ['ano', 'ipca_anual']

# 4. Preparar datas para o JOIN
df_vendas['data_venda'] = df_vendas['order_purchase_timestamp'].dt.normalize() # Remove a hora
df_vendas['ano'] = df_vendas['order_purchase_timestamp'].dt.year

# 5. O GRANDE JOIN
df_final = df_vendas.merge(df_dolar[['Data', 'cotacao_dolar']], left_on='data_venda', right_on='Data', how='left')
df_final['ano'] = df_final['ano'].astype(int)
df_ipca['ano'] = df_ipca['ano'].astype(int)
df_final = df_final.merge(df_ipca, on='ano', how='left')

# 6. Resolvendo os finais de semana (Forward Fill)
df_final = df_final.sort_values('order_purchase_timestamp')
df_final['cotacao_dolar'] = df_final['cotacao_dolar'].ffill()

if df_final['ipca_anual'].dtype == 'object':
    df_final['ipca_anual'] = df_final['ipca_anual'].astype(str).str.replace(',', '.')
    df_final['ipca_anual'] = pd.to_numeric(df_final['ipca_anual'], errors='coerce')

cols_datas_restantes = [
    'order_approved_at', 
    'order_delivered_carrier_date', 
    'order_delivered_customer_date', 
    'order_estimated_delivery_date'
]

for col in cols_datas_restantes:
    df_final[col] = pd.to_datetime(df_final[col], errors='coerce')

# 7. Salvar para o Power BI
df_final.to_csv('data_processada/vendas_indicadores_economicos.csv', index=False)
df_final.info()
