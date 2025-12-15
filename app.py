from flask import Flask, render_template, request
import feedparser
from googletrans import Translator
from datetime import datetime
import time

app = Flask(__name__)
translator = Translator()

# 擴展的 RSS 來源分類
RSS_FEEDS = {
    'headlines': [
        ('Google News', 'https://news.google.com/rss'),
        ('BBC', 'https://feeds.bbci.co.uk/news/rss.xml'),
        ('CNN', 'http://rss.cnn.com/rss/edition.rss'),
    ],
    'world': [
        ('Google News', 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB'),
        ('BBC World', 'https://feeds.bbci.co.uk/news/world/rss.xml'),
        ('CNN World', 'http://rss.cnn.com/rss/edition_world.rss'),
        ('Reuters', 'https://www.reutersagency.com/feed/?best-topics=world'),
    ],
    'politics': [
        ('BBC Politics', 'https://feeds.bbci.co.uk/news/politics/rss.xml'),
        ('CNN Politics', 'http://rss.cnn.com/rss/edition_politics.rss'),
    ],
    'business': [
        ('Google Business', 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB'),
        ('BBC Business', 'https://feeds.bbci.co.uk/news/business/rss.xml'),
        ('CNN Business', 'http://rss.cnn.com/rss/money_news_international.rss'),
    ],
    'tech': [
        ('Google Tech', 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB'),
        ('BBC Tech', 'https://feeds.bbci.co.uk/news/technology/rss.xml'),
        ('TechCrunch', 'https://techcrunch.com/feed/'),
        ('The Verge', 'https://www.theverge.com/rss/index.xml'),
    ],
    'sports': [
        ('BBC Sports', 'https://feeds.bbci.co.uk/sport/rss.xml'),
        ('ESPN', 'https://www.espn.com/espn/rss/news'),
    ],
    'entertainment': [
        ('BBC Entertainment', 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml'),
        ('E! News', 'https://www.eonline.com/syndication/feeds/rssfeeds/topstories.xml'),
    ],
    'health': [
        ('BBC Health', 'https://feeds.bbci.co.uk/news/health/rss.xml'),
        ('CNN Health', 'http://rss.cnn.com/rss/edition_health.rss'),
    ],
    'science': [
        ('BBC Science', 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml'),
        ('NASA', 'https://www.nasa.gov/rss/dyn/breaking_news.rss'),
    ],
}

# 分類中文名稱
CATEGORY_NAMES = {
    'headlines': '頭條新聞',
    'world': '國際',
    'politics': '政治',
    'business': '財經',
    'tech': '科技',
    'sports': '體育',
    'entertainment': '娛樂',
    'health': '健康',
    'science': '科學',
}

def translate_text(text):
    """翻譯文字為中文"""
    if not text:
        return ''
    try:
        result = translator.translate(text, dest='zh-tw')
        return result.text
    except:
        return text

def format_date(date_string):
    """格式化日期"""
    if not date_string:
        return ''
    try:
        # 嘗試解析 RSS 日期格式
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%Y-%m-%dT%H:%M:%S%z',
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_string, fmt)
                return dt.strftime('%Y-%m-%d %H:%M')
            except:
                continue
        return date_string[:16]
    except:
        return ''

def get_news(category='headlines', translate=False):
    """獲取指定分類的新聞"""
    articles = []
    feeds = RSS_FEEDS.get(category, RSS_FEEDS['headlines'])
    
    for source_name, feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # 每個來源取10條
                
                # 獲取內容摘要
                description = ''
                if hasattr(entry, 'summary'):
                    description = entry.summary
                elif hasattr(entry, 'description'):
                    description = entry.description
                
                # 清理 HTML 標籤
                import re
                description = re.sub('<[^<]+?>', '', description)
                description = description[:200] + '...' if len(description) > 200 else description
                
                # 獲取圖片
                image = ''
                if hasattr(entry, 'media_content') and entry.media_content:
                    image = entry.media_content[0].get('url', '')
                elif hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                    image = entry.media_thumbnail[0].get('url', '')
                elif hasattr(entry, 'enclosures') and entry.enclosures:
                    image = entry.enclosures[0].get('href', '')
                
                title = entry.get('title', '無標題')
                
                # 翻譯標題和摘要
                if translate:
                    title = translate_text(title)
                    description = translate_text(description)
                
                articles.append({
                    'title': title,
                    'description': description,
                    'url': entry.get('link', '#'),
                    'image': image,
                    'source': source_name,
                    'published': format_date(entry.get('published', '')),
                })
                
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")
            continue
    
    # 按時間排序
    articles.sort(key=lambda x: x['published'], reverse=True)
    return articles[:30]  # 返回最多30條

@app.route('/')
def index():
    category = request.args.get('category', 'headlines')
    translate = request.args.get('translate', 'false') == 'true'
    articles = get_news(category, translate)
    
    return render_template('index.html',
                         articles=articles,
                         categories=CATEGORY_NAMES,
                         current_category=category,
                         translate=translate)

if __name__ == '__main__':
    app.run(debug=True)
