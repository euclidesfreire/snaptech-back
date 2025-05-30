from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import pandas as pd

def collaborative_filtering(interactions, articles, user_id):

    # Supondo que 'interactions' seja a lista de objetos 'UserInteraction'
    data = [{
        'article_id': interaction.article_id,
        'liked': interaction.liked,
        'user_id': interaction.user_id
    } for interaction in interactions]

    # Criando o DataFrame
    df = pd.DataFrame(data)

    interaction_matrix = df.pivot_table(index='user_id', columns='article_id', values='liked', fill_value=0)

    print('interaction_matrix')
    print(interaction_matrix)
    
    # Similaridade entre usuários
    similarity_matrix = cosine_similarity(interaction_matrix)

    print('similarity_matrix')
    print(similarity_matrix)
    
    # Recomendar artigos
    user_index = interaction_matrix.index.get_loc(user_id)
    similar_users = similarity_matrix[user_index]

    print('user_index')
    print(user_index)

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