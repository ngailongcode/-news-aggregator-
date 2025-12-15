from flask import Flask, render_template, request
import feedparser
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

RSS_FEEDS = {
    'world': [
        ('Google News', 'https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en'),
        ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
        ('CNN', 'http://rss.cnn.com/rss/edition_world.rss'),
    ],
    'tech': [
        ('Google Tech', 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en'),
        ('BBC Tech', 'https://feeds.bbci.co.uk/news/technology/rss.xml'),
    ],
    'business': [
        ('Google Business', 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US:en'),
        ('BBC Business', 'https://feeds.bbci.co.uk/news/business/rss.xml'),
    ],
    'sports': [
        ('BBC Sports', 'https://feeds.bbci.co.uk/sport/rss.xml'),
        ('ESPN', 'https://www.espn.com/espn/rss/news'),
    ],
}

def translate_text(text):
    try:
        result = translator.translate(text, dest='zh-tw')
        return result.text
    except:
        return text

@app.route('/')
def index():
    category = request.args.get('category', 'world')
    translate = request.args.get('translate', 'off')
    
    articles = []
    feeds = RSS_FEEDS.get(category, RSS_FEEDS['world'])
    
    for source_name, feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            title = entry.title
            if translate == 'on':
                title = translate_text(title)
            articles.append({
                'title': title,
                'link': entry.link,
                'source': source_name
            })
    
    return render_template('index.html', 
                         articles=articles, 
                         category=category,
                         translate=translate,
                         categories=RSS_FEEDS.keys())

if __name__ == '__main__':
    app.run(debug=True)
