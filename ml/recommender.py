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
import time

from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

def cold_start_filtering(interactions, articles):
    metrics = pd.DataFrame()
    metrics = cold_start(interactions)

    print("Metrics")
    print(metrics)

    recommended_articles = metrics.head(20)

    return [articles[article_id] for article_id in recommended_articles.index]

def cold_start(interactions):

    interactions_dicts = [i.dict() for i in interactions]

    interactions_df = pd.DataFrame(interactions_dicts)

    #Agrupar por artigos mean e count
    metrics = interactions_df.groupby("article_id")[["like", "dislike"]].agg(["mean","count"])

    # Ajustar os nomes das colunas
    metrics.columns = ["mean_like", "count_like", "mean_dislike", "count_dislike"]

    # Total de interações
    metrics["total_interactions"] = metrics["count_like"] + metrics["count_dislike"]

    # Calcular score com log1p para suavizar impacto de artigos muito populares
    metrics["score"] = (metrics["mean_like"] - metrics["mean_dislike"]) * np.log1p(metrics["total_interactions"])

    metrics.sort_values("score", ascending=False, inplace=True)

    return metrics

def cluster_filtering(interactions, articles, user_id):

    metrics = pd.DataFrame()

    metrics = cold_start(interactions)

    interactions_dicts = [i.dict() for i in interactions]

    interactions_df = pd.DataFrame(interactions_dicts)

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

        return [articles[article_id] for article_id in recomendados['article_id']] 

def collaborative_filtering(interactions, articles, user_id):


    #if user_id not in interactions:
     #   return False
    # Supondo que 'interactions' seja a lista de objetos 'UserInteraction'

    metrics = pd.DataFrame()
    metrics = cold_start(interactions)

    interactions_dicts = [i.dict() for i in interactions]

    interactions_df = pd.DataFrame(interactions_dicts)
    
    interactions_df['score'] = interactions_df['article_id'].map(
        metrics['score']
    )

    if user_id not in interactions_df['user_id']:
        return False

    # Criando o DataFrame
    df = pd.DataFrame(interactions_df)

    interaction_matrix = df.pivot_table(index='user_id', columns='article_id', values='score', fill_value=0)
    
    # Similaridade entre usuários
    similarity_matrix = cosine_similarity(interaction_matrix)

    print('similarity_matrix')
    print(similarity_matrix)
    
    # Recomendar artigos
    user_index = interaction_matrix.index.get_loc(user_id)
    similar_users = similarity_matrix[user_index]

    print(f'Similar users to {user_id}:')
    print(similar_users)
    
    # Calcular os artigos recomendados com base na similaridade dos usuários
    similar_articles = interaction_matrix.T.dot(similar_users)  # soma ponderada das interações
    recommendations = similar_articles.sort_values(ascending=False).index.tolist()

    print(f'similar_articlesto {user_id}:')
    print(similar_articles)

    print(f'recommendations to {user_id}:')
    print(recommendations)

    # Filtrar artigos que o usuário já interagiu
    recommended_articles = [
        article_id for article_id in recommendations
        if interaction_matrix.loc[user_id, article_id] == 0  # Garantir que o valor da interação seja 0
    ]


    print(f'recommended_articles to {user_id}:')
    print(recommended_articles)

    
    # Retornar os artigos recomendados
    return [articles[article_id] for article_id in recommended_articles]