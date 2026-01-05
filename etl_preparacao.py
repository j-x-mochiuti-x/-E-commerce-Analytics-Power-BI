import pandas as pd
import os

DATA_PATH = 'data/'

# 1. Carregar Tabela de Pedidos 
df_orders = pd.read_csv(os.path.join(DATA_PATH, 'olist_orders_dataset.csv'))

# 2. Carregar Tabela de Itens 
df_items = pd.read_csv(os.path.join(DATA_PATH, 'olist_order_items_dataset.csv'))

# 3. Carregar Tabela de Clientes 
df_customers = pd.read_csv(os.path.join(DATA_PATH, 'olist_customers_dataset.csv'))

# 4. Carregar Tabela de Pagamentos 
df_payments = pd.read_csv(os.path.join(DATA_PATH, 'olist_order_payments_dataset.csv'))

# 5. Carregar Tabela de Produtos
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

if not os.path.exists('data_processada'):
    os.makedirs('data_processada')
df_completo.to_csv('data_processada/olist_master_data.csv', index=False)
