import pandas as pd
import os

# Caminho para os arquivos (ajuste se necessário)
DATA_PATH = 'data/'

# 1. Carregar Tabela de Pedidos (O Coração)
df_orders = pd.read_csv(os.path.join(DATA_PATH, 'olist_orders_dataset.csv'))

# 2. Carregar Tabela de Itens (Onde tem o Preço)
df_items = pd.read_csv(os.path.join(DATA_PATH, 'olist_order_items_dataset.csv'))

# 3. Carregar Tabela de Clientes (Quem comprou)
df_customers = pd.read_csv(os.path.join(DATA_PATH, 'olist_customers_dataset.csv'))

# 4. Carregar Tabela de Pagamentos (Como pagou)
df_payments = pd.read_csv(os.path.join(DATA_PATH, 'olist_order_payments_dataset.csv'))

# 5. Carregar Tabela de Produtos (O que é o produto)
df_products = pd.read_csv(os.path.join(DATA_PATH, 'olist_products_dataset.csv'))

# 6. Converter datas para o formato datetime
cols_date = ['order_delivered_customer_date', 'order_estimated_delivery_date', 'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date']
for col in cols_date:
    df_orders[col] = pd.to_datetime(df_orders[col])

# 7. Filtrar apenas pedidos Entregues ou Em trânsito
df_orders_clean = df_orders[df_orders['order_status'] !='canceled']
df_orders_clean = df_orders_clean[df_orders_clean['order_status'] !='unavailable']

# 8. Merge das tabelas para criar o DataFrame
df_completo = df_orders_clean.merge(df_items, on='order_id', how='inner')
df_completo = df_completo.merge(df_customers, on='customer_id', how='inner')
df_completo = df_completo.merge(df_products, on='product_id', how='inner')
df_completo['valor_total'] = df_completo['price'] + df_completo['freight_value']

# 9. Definir a data de referência
data_referencia = df_completo['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

# 10. Agrupar por cliente e calcular Recência, Frequência, Monetário
# Usamos 'nunique' para Frequency para contar pedidos únicos, não itens
df_rfm = df_completo.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (data_referencia - x.max()).days,
    'order_id': 'nunique',
    'valor_total': 'sum'
}).reset_index()

# 11. Renmeando colunas para RFM
df_rfm.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']

print('============= Análise RFM =============')
print(f"Número de clientes únicos processados: {df_rfm.shape[0]}")
print(df_rfm.sort_values('Monetary', ascending=False).head())