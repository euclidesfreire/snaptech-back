from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import pandas as pd

def collaborative_filtering(interactions, articles, user_id):
    # Construir matriz de interações
    df = pd.DataFrame(interactions)
    interaction_matrix = df.pivot_table(index='user_id', columns='article_id', values='liked', fill_value=0)
    
    # Similaridade entre usuários
    similarity_matrix = cosine_similarity(interaction_matrix)
    
    # Recomendar artigos
    user_index = interaction_matrix.index.tolist().index(user_id)
    similar_users = similarity_matrix[user_index]
    
    similar_articles = interaction_matrix.T.dot(similar_users)
    recommendations = similar_articles.sort_values(ascending=False).index.tolist()
    
    return [articles[article_id] for article_id in recommendations if article_id not in interaction_matrix.columns]
