# SNAPTECH API

## API NEWS
https://newsdata.io/dashboard

## Executar

- Criar venv
    python -m venv venv

- Entrar na venv
    - Linux
    source venv/bin/activate

    - Windows
    venv\Scripts\activate

- Instalar bibliotecas 
    pip install -r requirements.txt

- Executar fast-api
    uvicorn main:app --reload

## Artigos

- Dados
    - você usar o news.db ou news-copy.db já salvos
    - Ou carregar da API News Data
        - /fetch/latest
        - Se recarregar os artigos, em seguida precisa startar os dados exemplos
            - /start/

- Algoritmos de Recomendação
    ml/recommender.py

    - Para executar
        - Cold-start
            /recommendations/cold_start
        - Matrix de similaridade (precisa do email via post)
            /recommendations/