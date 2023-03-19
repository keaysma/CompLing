from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
import requests, json, re

"""
Download starting wikipedia page
Parse
Get all tokens in order
Find all links
Rinse and repeat
"""

BASE_URL = "https://en.wikipedia.org"
STARTING_URL = "/wiki/Philosophy"
PAGES_TO_READ = 40

Tokens = List[str]
Links = List[str]
PageData = Tuple[Tokens, Links]

BAD_TOKENS = [":", "Main_page", ".jpeg", ".jpg", ".png", ".php", "(disambiguation)"]
def is_real_page(path: str) -> bool:
    return path.startswith('/wiki') \
            and not any(list(map(lambda t: t in path, BAD_TOKENS)))

t = "This is a[45] test. Of the system, and Michael-Andrew says: \"it's pretty great!\""
def tokenize(text: str) -> List[str]:
    tokens = []
    token = ""
    for char in text:
        if re.match(r"[A-Za-z-/']+", char):
            token += char
            continue
        if token:
            tokens.append(token)
            token = ""
        if re.match(r"[.?!:,~\"]+", char):
            tokens.append(char)
    if token:
        tokens.append(token)
        token = ""
    return tokens

def download_page(url: str) -> PageData:
    res = requests.get(url)
    print(f"{res=}")
    
    soup = BeautifulSoup(res.text)
    ps = soup.find_all('p')
    #print(f"{soup=}")

    tokens = tokenize(' '.join([p.text for p in ps])) #soup.text.split()

    links = soup.find_all('a')
    all_hrefs = [l.get('href') for l in links]
    external_hrefs = [h for h in all_hrefs if h and h.startswith('http')]
    page_hrefs = [h for h in all_hrefs if h and is_real_page(h)]
    
    return (tokens, page_hrefs)

def read_local_page(url: str) -> Optional[PageData]:
    parsed_url = url.replace("/", "\\")
    try:
        data = json.load(open(f'./data/{parsed_url}.json', 'r'))
        return (data['tokens'], data['links'])
    except: 
        return None
    
def write_local_page(url: str, page_data: PageData) -> None:
    parsed_url = url.replace("/", "\\")
    with open(f'./data/{parsed_url}.json', 'w') as f:
        f.write(
            json.dumps({
                "tokens": page_data[0],
                "links": page_data[1]
            })
        )

def get_page(url: str) -> PageData:
    if page_data := read_local_page(url):
        return page_data
    downloaded_page_data = download_page(url)
    write_local_page(url, downloaded_page_data)
    return downloaded_page_data

if __name__ == '__main__':
    text, links = get_page(BASE_URL + STARTING_URL)

    pages_read = 0
    while pages_read < PAGES_TO_READ:
        link = links.pop(0)
        _, new_links = get_page(BASE_URL + link)
        links += new_links
        pages_read += 1

    print(len(links))
