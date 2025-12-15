from flask import Flask, render_template
import feedparser

app = Flask(__name__)

RSS_FEEDS = [
    'https://news.google.com/rss',
    'https://feeds.bbci.co.uk/news/rss.xml'
]

@app.route('/')
def index():
    articles = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            articles.append({
                'title': entry.title,
                'link': entry.link,
                'source': feed.feed.title
            })
    return render_template('index.html', articles=articles)

if __name__ == '__main__':
    app.run(debug=True)
