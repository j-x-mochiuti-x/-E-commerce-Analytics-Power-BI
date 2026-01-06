import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 1. Carregar os dados
df = pd.read_csv(r'data_processada/clientes_segmentados.csv')

# 2. Selecionar apenas as variáveis base (RFM) para o PCA
# Não usamos os Scores ou IDs, apenas os valores reais
features = ['Recency', 'Frequency', 'Monetary']
x = df[features]

# 3. Padronizar os dados (Obrigatório para o PCA funcionar bem)
x_scaled = StandardScaler().fit_transform(x)

# 4. Aplicar o PCA para 3 componentes
pca = PCA(n_components=3)
principais_componentes = pca.fit_transform(x_scaled)

# 5. Criar um novo DataFrame com os resultados
df_pca = pd.DataFrame(data=principais_componentes, 
                      columns=['PC1', 'PC2', 'PC3'])

# 6. Trazer de volta a identificação do Cluster para colorir
df_pca['Cluster'] = df['Cluster']
df_pca['Segmento'] = df['RFM_Segmento'] 

# 7. Gerar o gráfico 3D Interativo
fig = px.scatter_3d(
    df_pca, x='PC1', y='PC2', z='PC3',
    color='Cluster',
    title='Visualização 3D - Segmentação de Clientes (PCA)',
    labels={'PC1': 'Impacto Financeiro/Freq', 'PC2': 'Recência', 'PC3': 'Variância Extra'},
    opacity=0.8,
    hover_data=['Segmento'] # Mostra o nome do segmento ao passar o mouse
)

fig.update_layout(template='plotly_dark') # Mantém o seu estilo Dark Mode
fig.show()