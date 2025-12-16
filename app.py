from flask import Flask, jsonify, request, render_template
import requests
import re
from datetime import datetime
import urllib.parse

app = Flask(__name__)

# 新聞分類
CATEGORY_FEEDS = {
    'headlines': [
        {'url': 'https://feeds.bbci.co.uk/news/rss.xml', 'name': 'BBC'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml', 'name': 'NYT'}
    ],
    'business': [
        {'url': 'https://feeds.bbci.co.uk/news/business/rss.xml', 'name': 'BBC Business'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml', 'name': 'NYT Business'}
    ],
    'tech': [
        {'url': 'https://feeds.bbci.co.uk/news/technology/rss.xml', 'name': 'BBC Tech'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml', 'name': 'NYT Tech'}
    ],
    'entertainment': [
        {'url': 'https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml', 'name': 'BBC Entertainment'}
    ],
    'sports': [
        {'url': 'https://feeds.bbci.co.uk/sport/rss.xml', 'name': 'BBC Sport'}
    ],
    'world': [
        {'url': 'https://feeds.bbci.co.uk/news/world/rss.xml', 'name': 'BBC World'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/World.xml', 'name': 'NYT World'}
    ],
    'health': [
        {'url': 'https://feeds.bbci.co.uk/news/health/rss.xml', 'name': 'BBC Health'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Health.xml', 'name': 'NYT Health'}
    ],
    'science': [
        {'url': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml', 'name': 'BBC Science'},
        {'url': 'https://rss.nytimes.com/services/xml/rss/nyt/Science.xml', 'name': 'NYT Science'}
    ]
}

def parse_xml(xml_text):
    """簡易 XML 解析"""
    items = []
    item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
    
    for match in item_pattern.finditer(xml_text):
        item_content = match.group(1)
        
        def get_tag(tag):
            # 處理 CDATA
            pattern = re.compile(f'<{tag}[^>]*><!\\[CDATA\\[(.*?)\\]\\]></{tag}>|<{tag}[^>]*>(.*?)</{tag}>', re.DOTALL)
            m = pattern.search(item_content)
            if m:
                return (m.group(1) or m.group(2) or '').strip()
            return ''
        
        title = get_tag('title')
        link = get_tag('link')
        description = re.sub(r'<[^>]+>', '', get_tag('description'))[:200]
        pub_date = get_tag('pubDate')
        
        if title:
            items.append({
                'title': title,
                'link': link,
                'description': description,
                'pubDate': pub_date
            })
    
    return items

def format_date(date_str):
    """格式化日期"""
    try:
        dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        try:
            dt = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str

def translate_text(text):
    """使用 Google 翻譯 API"""
    if not text or text.strip() == '':
        return text
    
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-TW&dt=t&q={urllib.parse.quote(text)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and data[0]:
                translated = ''
                for part in data[0]:
                    if part[0]:
                        translated += part[0]
                return translated if translated else text
        
        return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/news')
def get_news():
    category = request.args.get('category', 'headlines')
    feeds = CATEGORY_FEEDS.get(category, CATEGORY_FEEDS['headlines'])
    
    all_articles = []
    
    for feed in feeds:
        try:
            response = requests.get(feed['url'], timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; NewsAggregator/1.0)'
            })
            
            if response.status_code == 200:
                items = parse_xml(response.text)
                
                for item in items[:10]:
                    all_articles.append({
                        'title': item['title'],
                        'description': item['description'],
                        'url': item['link'],
                        'source': feed['name'],
                        'published': format_date(item['pubDate']),
                        'category': category
                    })
        except Exception as e:
            print(f"Error fetching {feed['name']}: {e}")
    
    return jsonify({
        'success': True,
        'category': category,
        'articles': all_articles[:30]
    })

@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        title = data.get('title', '')
        description = data.get('description', '')
        
        print(f"Translating: {title[:50]}")
        
        translated_title = translate_text(title)
        translated_description = translate_text(description)
        
        print(f"Translated to: {translated_title[:50]}")
        
        return jsonify({
            'success': True,
            'translated_title': translated_title,
            'translated_description': translated_description
        })
    except Exception as e:
        print(f"Translate API error: {e}")
        return jsonify({
            'success': False,
            'translated_title': data.get('title', ''),
            'translated_description': data.get('description', ''),
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)