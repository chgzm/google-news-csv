import sys
import csv
import requests
import bs4
from fake_useragent import UserAgent
from argparse import ArgumentParser

def gen_csv(articles, out):
    if out is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=['Title', 'URL'], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(articles)
    else:
        with open(out, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['Title', 'URL'], quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(articles)

def get_articles(keyword, num, lang, full):
    url = 'https://www.google.com/search?q={}&hl={}&gl=jp&num={}&pws=0&tbm=nws'.format(keyword, lang, num + 10)
    ua = UserAgent()

    res = requests.get(url, headers={'User-Agent': ua.chrome})
    res.raise_for_status()

    bs = bs4.BeautifulSoup(res.text, 'html.parser')

    div_list  = bs.find_all("div", {"role" : "heading"})
    a_list = bs.select("div.dbsr > a")

    articles = [] 
    for i, (div, a) in enumerate(zip(div_list, a_list)):
        title_str = div.string
        if full and "..." in title_str:
            res_link_dst = requests.get(a.get('href'), headers={'User-Agent': ua.chrome})

            bs4_link_dst = bs4.BeautifulSoup(res_link_dst.text, 'html.parser')
            title = bs4_link_dst.find('title').text       
            title_str = title.replace("\n", "").split("|")[0]

        articles.append({
            'Title': title_str,
            'URL': a.get('href')
        })

        if num <= (i + 1):
            break

    return articles

def parse_argument():
    argparser = ArgumentParser()
    argparser.add_argument("keyword", help="search keyword", type=str, default=None)
    argparser.add_argument("-n", "--num", help="specify the number of articles to be scraped", type=int, default=50)
    argparser.add_argument("-l", "--lang", help="specify the language", default='ja')
    argparser.add_argument("-o", "--out", help="specify output file name", default=None)
    argparser.add_argument("-f", "--full", help="get the entire title if it's omitted.", action='store_true')

    return argparser.parse_args()
 
def main():
    args = parse_argument()
    articles = get_articles(args.keyword, args.num, args.lang, args.full) 
    gen_csv(articles, args.out)

if __name__ == '__main__':
    main()
