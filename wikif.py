import wikipediaapi, requests, re
from bs4 import BeautifulSoup



def getWikiPage(input):
        
    payload = {
        'q': input
    }
    googleResultPage = requests.get('https://www.google.com/search', params=payload)

    print(googleResultPage.status_code)
    googleSoup = googleResultPage.text

    googleSoup = BeautifulSoup(googleSoup, 'html.parser')
    resultContainer = googleSoup.find_all('a')

    #form a regex and get the title from the first url that matched

    wikiTitleRegex = re.compile(r"(/url\?q=https://en.wikipedia.org/wiki/)([\(\)A-Za-z_%]+)&[A-Za-z=]+")
    #parse the page title from google url
    wikiTitle = None
    for item in resultContainer:
        wikiTitles = wikiTitleRegex.match(item['href'])
        if wikiTitles:
            wikiTitle = wikiTitles.group(2)
            break

    #get the page
    if wikiTitle:
        wiki = wikipediaapi.Wikipedia('en')
        page = wiki.page(wikiTitle)
        return page
    else:
        return None
