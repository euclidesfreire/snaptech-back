from newsdataapi import NewsDataApiClient

class Article:

    def __init__(self, title, modelo, ano):
        self.article_id = article_id
        self.title = title
        self.link = link
        self.description = description
        self.image_url = image_url
        self.pubDate = pubDate
        self.sentiment = sentiment
        self.sentiment_stats = sentiment_stats

def get_articles(q = "", country = "br", category = "technology"):

    # API key authorization, Initialize the client with your API key
    api = NewsDataApiClient(apikey="pub_624603223c8e181a61bcd17adc1b2a82cdaa8")

    # You can paginate till last page by providing "page" parameter
    page=None

    while True:

        response = api.news_api(q = q, page = page, country = country)

        print(response)

        page = response.get('nextPage',None)

        if not page:
            break

get_articles()