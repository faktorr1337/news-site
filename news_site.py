from flask import Flask, render_template_string
import feedparser
from bs4 import BeautifulSoup
import datetime

app = Flask(__name__)

def get_news():
    rss_url = "https://habr.com/ru/rss/news/?fl=ru"
    feed = feedparser.parse(rss_url)
    
    news_list = []
    for entry in feed.entries[:6]:  # Берем 6 новостей (1 главная + 5 справа)
        # 1. Очищаем текст от HTML-тегов
        soup = BeautifulSoup(entry.summary, "html.parser")
        clean_text = soup.get_text()
        
        # 2. Ищем картинку в тексте новости
        img_tag = soup.find('img')
        img_url = img_tag['src'] if img_tag else ""

        # 3. Красиво форматируем дату
        try:
            pub_date = entry.published_parsed
            formatted_date = datetime.datetime(*pub_date[:6]).strftime("%d.%m.%Y")
        except:
            formatted_date = entry.published

        news_list.append({
            "title": entry.title,
            "text": clean_text[:300] + "...", # Чуть увеличил текст для главной
            "link": entry.link,
            "date": formatted_date,
            "image": img_url
        })
    return news_list

@app.route("/")
def home():
    news = get_news()
    html = """
    <!doctype html>
    <html>
        <body style="font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; padding: 20px; max-width: 1200px; margin: 0 auto;">
            <h1 style="text-align: center; color: #4CAF50; margin-bottom: 30px;">📰 Новостная витрина</h1>
            
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                
                <!-- ЛЕВАЯ КОЛОНКА (Главная новость) -->
                <div style="flex: 2; min-width: 300px; background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    {% if news[0].image %}
                        <img src="{{ news[0].image }}" style="width: 100%; max-height: 400px; object-fit: cover; border-radius: 8px; margin-bottom: 20px;">
                    {% endif %}
                    <h1 style="color: white; margin-top: 0;">{{ news[0].title }}</h1>
                    <p style="color: #888;">{{ news[0].date }}</p>
                    <p style="color: #ccc; font-size: 18px; line-height: 1.6;">{{ news[0].text }}</p>
                    <a href="{{ news[0].link }}" target="_blank" style="display: inline-block; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Читать полностью →</a>
                </div>

                <!-- ПРАВАЯ КОЛОНКА (Остальные новости) -->
                <div style="flex: 1; min-width: 250px; display: flex; flex-direction: column; gap: 15px;">
                    {% for news_item in news[1:] %}
                        <div style="background: #1e1e1e; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                            <h3 style="margin-top: 0; color: white; font-size: 16px;">{{ news_item.title }}</h3>
                            <p style="color: #888; font-size: 12px;">{{ news_item.date }}</p>
                            <a href="{{ news_item.link }}" target="_blank" style="color: #4CAF50; text-decoration: none; font-size: 14px;">Читать →</a>
                        </div>
                    {% endfor %}
                </div>
                
            </div>
        </body>
    </html>
    """
    return render_template_string(html, news=news)

if __name__ == "__main__":
    app.run(debug=True)