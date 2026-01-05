import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# 1. Carregar os dados processados no ETL
PATH_DADOS = 'data_processada/olist_master_data.csv'
df_completo = pd.read_csv(PATH_DADOS, parse_dates=['order_purchase_timestamp'])

print("✅ Dados carregados com sucesso!")

# 2. Definir a data de referência (Snapshot)
data_referencia = df_completo['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

# 3. Agrupar por cliente e calcular R, F, M
df_rfm = df_completo.groupby('customer_unique_id').agg({
    'order_purchase_timestamp': lambda x: (data_referencia - x.max()).days,
    'order_id': 'nunique',
    'valor_total': 'sum'
}).reset_index()

df_rfm.columns = ['customer_unique_id', 'Recency', 'Frequency', 'Monetary']

# 4. Gerando Scores de 1 a 5 (Tratando o erro de duplicatas na Frequência)
df_rfm['R_Score'] = pd.qcut(df_rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)
df_rfm['F_Score'] = pd.qcut(df_rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)
df_rfm['M_Score'] = pd.qcut(df_rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)

# Score de Segmento
df_rfm['RFM_Segmento'] = df_rfm['R_Score'].astype(str) + df_rfm['F_Score'].astype(str) + df_rfm['M_Score'].astype(str)

# 5. Preparação para o Machine Learning
scaler = StandardScaler()
dados_cluster = df_rfm[['Recency', 'Frequency', 'Monetary']]
dados_scaled = scaler.fit_transform(dados_cluster)

# 6. K-Means (4 Grupos)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_rfm['Cluster'] = kmeans.fit_predict(dados_scaled)

# 7. Salvar o resultado final para o Power BI
df_rfm.to_csv('data_processada/clientes_segmentados.csv', index=False)

# 8. Analisar os Clusters
analise_clusters = df_rfm.groupby('Cluster').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': 'mean',
    'customer_unique_id': 'count'
}).round(2).sort_values('Monetary', ascending=False)

print(analise_clusters)