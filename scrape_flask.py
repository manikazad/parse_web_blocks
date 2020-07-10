import scrapper
import spider

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def main():
    return "Hello, I am Web Scrapper"

@app.route('/scrape')
def scrape_all():
    url_list = request.json['url']
    for url in url_list:
        urls, page_content = spider.traverse_domain_bfs(url, max_depth=1)




@app.route('/leadership_scrape')
def scrape_leadership():
     url_list = request.json['url']

     for url in url_list:
         pass
