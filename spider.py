


import urllib.request as urllib2
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from simplediff import diff
import signal
import pymongo
from contextlib import contextmanager
from settings import *



@contextmanager
def timeout(time):
    # Register a function to raise a TimeoutError on the signal.
    signal.signal(signal.SIGALRM, raise_timeout)
    # Schedule the signal to be sent after ``time``.
    signal.alarm(time)

    try:
        yield
    except TimeoutError:
        pass
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError


flatten = lambda l: [item for sublist in l for item in sublist]
filter_stop = lambda x : True if len(x) > 2 else False
dictify = lambda x: dict([(str(i), l)for i, l in enumerate(x)])


def get_domain(url):
    parsed_uri = urlparse(url)
    domain_name = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain_name


class Spider():
    def __init__(self, mongo_client):

        self.mongo_client = mongo_client
        self.mongo_db = mongo_client[crawl_db]
        self.webpage_col = self.mongo_db[web_page_collection]
        self.webpage_tracker_col = self.mongo_db[crawl_tracker]


    def url_opener(self, url):
        agents = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6'}
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(auth, urllib2.HTTPHandler)
        page = opener.open(url).read()
        return page


    def get_page_record(self, link, depth):
        mongo_page = self.webpage_col.find({"url": link})
        if mongo_page.count() != 0:
            mongo_record = mongo_page.next()
        else:
            page = self.url_opener(link)
            page_urls = self.correct_url_list(self.extractLinks(page), link)
            iter_list = set([url.strip('/') for url in page_urls if not url.endswith(invalid_suffix) and not url.startswith(invalid_prefix)])

            mongo_record = dict()
            mongo_record["url"] = link
            mongo_record["content"] = page
            mongo_record["links"] = dictify(iter_list)
            mongo_record["depth"] = depth
            mongo_record["domain"] = get_domain(link)
            mongo_record["parent_url"] = link
            self.webpage_col.insert(mongo_record)

        return mongo_record


    def getPage(self, link, depth):
        with timeout(20):
            if not link.startswith("http"):
                try:
                    newlink = "https://" + link
                    page_record = self.get_page_record(newlink, depth)
                    return page_record

                except Exception as e:
                    newlink = "http://" + link
                    page_record = self.get_page_record(newlink, depth)
                    return page_record

            else:
                page_record = self.get_page_record(link, depth)
                return page_record


    def extractLinks(self, html, link_ext='.txt'):
        soup = BeautifulSoup(html, features="lxml")
        linktags = soup.findAll('a')
        links = []
        for tags in linktags:
            link = tags.get('href', None)
            links.append(link)
        return links





    def correct_url_list(self, url_list, parent_url):
        correct_url_list = []
        parent_parsed = urlparse(parent_url)
        for url in url_list:
            url_parsed = urlparse(url)
            dif = set([d[1] for d in diff(parent_parsed.netloc, url_parsed.netloc) if d[0] in ('+', '-')])
            if url_parsed.netloc == '':
                url = '{uri.scheme}://{uri.netloc}'.format(uri=parent_parsed) + "/" + url_parsed.path
                correct_url_list.append(url)

            elif url_parsed.netloc == parent_parsed.netloc or dif in ['www.']:
                correct_url_list.append(url)
        return correct_url_list


    def traverse_domain_bfs(self, domain_url, max_depth=5):
        master_dict = {}

        domain_url = domain_url.strip("/")
        master_list = []
        print("Opening URL:", domain_url)
        try:

            page_record = self.getPage(domain_url, 0)
            raw_page = page_record['content']
            domain_url = page_record['url']
            iter_list = [url for id, url in page_record['links'].items()]

            master_dict[domain_url] = raw_page
            print("Fetched URL data")
            master_list = {domain_url}
            print("Extracted", len(iter_list), "urls from the site", sep=' ')

            master_list = master_list.union(iter_list)

            for depth in range(max_depth):
                next_iter_list = []
                print("DIVING AT DEPTH:", depth)
                for iter_url in iter_list:
                    try:
                        print("Trying to open: ", iter_url, "\t", end= "\r",flush=True)
                        iter_page_record = self.getPage(iter_url ,depth)

                        iter_raw_page= iter_page_record['content']
                        iter_url = iter_page_record['url']
                        valid_url_list = [url for id, url in iter_page_record['links'].items()]

                        master_dict[iter_url] = iter_raw_page
                        valid_url_list = set([url.strip('/') for url in valid_url_list if url.strip("/") not in master_list])
                        next_iter_list += valid_url_list
                        master_list = master_list.union(valid_url_list)

                    except Exception as e:
                        print("ERROR in processing url: ", iter_url, e, e.__traceback__)
                        continue

                iter_list = next_iter_list

            return master_list, master_dict

        except Exception as e:
            print("Error processing the URL ", domain_url, " : ", e)
            return master_list, master_dict


if __name__ == "__main__":

    client = pymongo.MongoClient("mongodb://" + mongo_host + ":"+ mongo_port+ "/")
    url = "https://www.shreecement.com"
    spider= Spider(client)
    urls, content= spider.traverse_domain_bfs(url, max_depth=2)
    client.close()