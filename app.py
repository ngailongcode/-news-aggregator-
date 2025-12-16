from flask import Flask, render_template, request, jsonify
import feedparser
from datetime import datetime
import time
from googletrans import Translator

app = Flask(__name__)

# RSS 來源
RSS_FEEDS = {
    '全部': [],
    '財經': [
        ('Bloomberg', 'https://feeds.bloomberg.com/markets/news.rss'),
        ('Reuters Business', 'https://feeds.reuters.com/reuters/businessNews'),
        ('CNBC', 'https://www.cnbc.com/id/10001147/device/rss/rss.html'),
    ],
    '科技': [
        ('TechCrunch', 'https://techcrunch.com/feed/'),
        ('The Verge', 'https://www.theverge.com/rss/index.xml'),
        ('Wired', 'https://www.wired.com/feed/rss'),
    ],
    '娛樂': [
        ('Variety', 'https://variety.com/feed/'),
        ('Hollywood Reporter', 'https://www.hollywoodreporter.com/feed/'),
        ('Entertainment Weekly', 'https://ew.com/feed/'),
    ],
    '體育': [
        ('ESPN', 'https://www.espn.com/espn/rss/news'),
        ('BBC Sport', 'https://feeds.bbci.co.uk/sport/rss.xml'),
        ('Sky Sports', 'https://www.skysports.com/rss/12040'),
    ],
    '國際': [
        ('BBC', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
        ('CNN', 'http://rss.cnn.com/rss/edition_world.rss'),
        ('Al Jazeera', 'https://www.aljazeera.com/xml/rss/all.xml'),
    ],
}

translator = Translator()

def fetch_news(category='全部'):
    articles = []
    
    if category == '全部':
        feeds_to_fetch = []
        for cat, feeds in RSS_FEEDS.items():
            if cat != '全部':
                feeds_to_fetch.extend(feeds)
    else:
        feeds_to_fetch = RSS_FEEDS.get(category, [])
    
    for source_name, feed_url in feeds_to_fetch:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                pub_date = ''
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M')
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6]).strftime('%Y-%m-%d %H:%M')
                
                articles.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'summary': entry.get('summary', '')[:200] + '...' if entry.get('summary') else '',
                    'source': source_name,
                    'published': pub_date
                })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            continue
    
    articles.sort(key=lambda x: x['published'], reverse=True)
    return articles[:30]

@app.route('/')
def index():
    category = request.args.get('category', '全部')
    articles = fetch_news(category)
    categories = list(RSS_FEEDS.keys())
    current_time = datetime.now().strftime('%m月%d日 下午%H:%M')
    return render_template('index.html', 
                         articles=articles, 
                         categories=categories, 
                         current_category=category,
                         update_time=current_time)

@app.route('/translate', methods=['POST'])
def translate_text():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if text:
            result = translator.translate(text, dest='zh-tw')
            return jsonify({'translated': result.text})
        return jsonify({'translated': text})
    except Exception as e:
        print(f"Translation error: {e}")
        return jsonify({'translated': text, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)