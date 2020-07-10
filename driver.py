import spider
import scrapper
import pymongo
import pandas as pd
from settings import *

dat = pd.read_csv("./Indian-Male-Names.csv")
flatten = lambda l: [item for sublist in l for item in sublist]
filter_stop = lambda x : True if len(x) > 2 else False

names_list = list(set(flatten(list(map(lambda x : str(x).split(), list(dat['name']))))))
leadership_dict = ['manage', 'team', 'president', 'chief', 'leadership', 'leader', 'executive', 'operating', 'ceo', \
                   'coo', 'cfo','secretary', 'personnel', 'head', 'management']
prod_service_dict = ['product', 'offer', 'offering', 'service', 'serv', 'business', 'prod', 'services', 'products', ]

filter_out = ['media', 'press', 'release', 'report', 'releases', 'award', 'function', 'prize', 'money', 'career', \
              'job', 'consumer', 'customer', 'user', 'contact', 'office', 'careers', 'policy', 'privacy', 'employment',\
              'news', 'events', 'recruit', 'recruitment', 'research']



mongo_client = pymongo.MongoClient("mongodb://" + mongo_host + ":"+ mongo_port+ "/")
web_crawl_db = mongo_client[crawl_db]
web_pages_col = web_crawl_db[web_page_collection]
text_cont_col = web_crawl_db[text_content_collection]

leader_col = web_crawl_db[leadership_content_collection]
product_col = web_crawl_db[product_content_collection]

def get_mongo_records(mongo_client, db_name, col_name, key, value):
    mongo_db = mongo_client[db_name]
    mongo_collection = mongo_db[col_name]
    mongo_records = mongo_collection.find({key: value})
    return mongo_records


def put_mongo_records(mongo_client, db_name, col_name, records):
    mongo_record_ids = []
    mongo_db = mongo_client[db_name]
    mongo_collection = mongo_db[col_name]
    if type(records) == list:
        if records != []:
            mongo_record_ids = mongo_collection.insert_many(records)
    else:
        if records != {}:
            mongo_record_ids = mongo_collection.insert(records)

    return mongo_record_ids


def get_clean_text_blocks(web_pages):

    scraped_text_collection = []
    for url, content in web_pages.items():
        url_text_record = {}
        mongo_record = text_cont_col.find({"url": url})
        if mongo_record.count() != 0:
            text_blocks = mongo_record.next()['content']
        else:
            text_blocks = scrapper.scrap_for_text(content)
            url_text_record['url'] = url
            url_text_record['content'] = text_blocks

        content_classify(url, text_blocks)
        scraped_text_collection.append(url_text_record)
    return scraped_text_collection


def content_classify(url, text_blocks):
    leader_flag = False
    product_flag = False
    leadership_record = {}
    leadership_record['domain'] = spider.get_domain(url)
    leadership_record['url'] = url
    leadership_record['content'] = []

    product_record = {}
    product_record['domain'] = spider.get_domain(url)
    product_record['url'] = url
    product_record['content'] = []

    leader_mongo = leader_col.find({"url": url})
    product_mongo = product_col.find({"url": url})

    for block in text_blocks:
        block_text = []
        for line in block:
            block_text.extend(line)

        content = list(filter(filter_stop, flatten([i.lower().split() for i in block_text])))

        if leader_mongo.count() == 0:
            if len(set(leadership_dict).intersection(content)) >= 3 and len(set(filter_out).intersection(content)) < 5:
                if len(set(content).intersection(names_list)) > 1:
                    leadership_record['content'].append(block)
                    leader_flag = True

        if product_mongo.count() == 0:
            if len(set(prod_service_dict).intersection(content)) > 2 and len(set(filter_out).intersection(content)) < 5:
                product_flag = True
                product_record['content'].append(block)

    if leader_flag:
        put_mongo_records(mongo_client, crawl_db, leadership_content_collection, leadership_record)

    if product_flag:
        put_mongo_records(mongo_client, crawl_db, product_content_collection, product_record)


def crawl_n(start = 0, end= -1):


    crawl_list = pd.read_csv("./website_list.csv")
    for url in crawl_list["Company website address"][start:end]:
        s = spider.Spider(mongo_client)
        urls, page_contents = s.traverse_domain_bfs(url, max_depth=1)
        clean_text_col = get_clean_text_blocks(page_contents)
        insert_ids = put_mongo_records(mongo_client, "web_crawl", "web_text_content", clean_text_col)


def crawl_one(url):
    s = spider.Spider(mongo_client)
    urls, page_contents = s.traverse_domain_bfs(url, max_depth=1)
    clean_text_col = get_clean_text_blocks(page_contents)
    insert_ids = put_mongo_records(mongo_client, "web_crawl", "web_text_content", clean_text_col)


if __name__ == "__main__":
    # main(start=0, end=1)

    crawl_n(start = 245)
