import asyncio
from typing import List, Optional
from pydantic import BaseModel
import numpy as np
import pandas as pd
import random
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances

def cold_start(interactions):
    #Agrupar por artigos mean e count
    metrics = interactions.groupby("article_id")[["like", "dislike"]].agg(["mean","count"])

    # Ajustar os nomes das colunas
    metrics.columns = ["mean_like", "count_like", "mean_dislike", "count_dislike"]

    # Total de interações
    metrics["total_interactions"] = metrics["count_like"] + metrics["count_dislike"]

    # Calcular score com log1p para suavizar impacto de artigos muito populares
    metrics["score"] = (metrics["mean_like"] - metrics["mean_dislike"]) * np.log1p(metrics["total_interactions"])

    metrics.sort_values("score", ascending=False, inplace=True)

    return metrics['score']

def collaborative_filtering(interactions, user_id):

    metrics = cold_start(interactions);

    #Agrupar por artigos mean e count
    interactions['score'] = interactions_df['article_id'].map(
        metrics['score']
    )

    # Cria matriz user x article (cada célula: score)
    interactions_matrix = interactions_df.pivot_table(
        index='article_id',
        columns='user_id',
        values='score',
        fill_value=0
    )

    # Padronização
    scaled = StandardScaler().fit_transform(interactions_matrix)

    # PCA
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(scaled)

    # Clustering
    kmeans = KMeans(n_clusters=5, random_state=42)
    clusters = kmeans.fit_predict(reduced)

    # Criar um novo DataFrame com os componentes principais
    pca_df = pd.DataFrame(reduced, columns=['PC1', 'PC2'])
    pca_df['article_id'] = interactions_matrix.index  

    # Adiciona os clusters ao novo DataFrame
    pca_df['cluster'] = clusters

    # Adiciona os clusters ao DataFrame
    interactions_matrix['cluster'] = clusters


    # Suponha que você ainda tem o DataFrame original
    # interactions_df: com colunas ['user_id', 'article_id', 'score']
    # pca_df: com ['PC1', 'PC2', 'article_id']

    # 1. Pega os artigos com score > 0 desse usuário
    artigos_usuario = interactions_df[
        (interactions_df['user_id'] == user_id) &
        (interactions_df['score'] > 0)
    ]

    # 2. Junta com pca_df para pegar os vetores PCA dos artigos que ele interagiu
    vetores_curtidos = artigos_usuario.merge(pca_df, on='article_id')[['PC1', 'PC2']]

    # 3. Se o usuário não interagiu com nada
    if vetores_curtidos.empty:
        return False
    else:
        # 4. Média dos vetores dos artigos com maior score
        centro_usuario = vetores_curtidos.mean().values.reshape(1, -1)

        # 5. Calcula a distância de todos os artigos em pca_df até esse ponto
        vetores_todos = pca_df[['PC1', 'PC2']].values
        distancias = euclidean_distances(vetores_todos, centro_usuario)

        # 6. Adiciona as distâncias ao DataFrame
        pca_df['distancia'] = distancias

        # 7. Remove os artigos que o usuário já viu
        artigos_vistos = artigos_usuario['article_id'].tolist()
        pca_df_filtrado = pca_df[~pca_df['article_id'].isin(artigos_vistos)]

        # 8. Ordena pelas distâncias (os mais próximos ao perfil do usuário)
        recomendados = pca_df_filtrado.sort_values(by='distancia')

        return recomendados 