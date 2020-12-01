import requests
from bs4 import BeautifulSoup

from .utils import saveDict, loadDict

class WordManager:
    #I am Michael, I love Raquel, I eat protien, etc...
    rules, words = {}, {}
    parts_of_speach = {
        'determiner'          :        'd',
        'noun'                :        'n',
        'pronoun'             :        'pn',
        'preposition'         :        'p',
        'verb'                :        'v',
        'transitive verb'     :        'v', #vt
        'intransitive verb'  :         'v', #vi
        'ditransitive verb'  :         'v', #vd
        'adjective'           :        'adj',
        'adverb'              :        'adv',
        'conjunction'         :        'conj',
    }

    def __init__(self):
        print('new tree')
        self.rules = loadDict('rules.json')
        self.words = loadDict('local_bank.json')
        
    def saveWordClasses(self):
        saveDict(self.words, 'local_bank.json')
    
    def fetchLikelyClass(self, word = None, rid_url = None):
        url = "https://www.wordsmyth.net/?level=3&ent={}".format(word) if word else rid_url
        s = requests.Session()
        res = s.get(url, verify = False)
        
        likely_class = None
        soup = BeautifulSoup(res.text, 'html5lib')
        
        # There are multiple parts of speech of the word, and just one definition
        '''
        mainlist = soup.findAll("dl", {"class": "mainlist"})
        if len(mainlist) == 1:
            many_parts_of_speech_title = mainlist[0].findAll("dt", text='parts of speech:')
            if len(many_parts_of_speech_title) == 1:
                many_parts_of_speech = many_parts_of_speech_title[0].findNext("dd")
                return [_.text for _ in mpos.findAll("a")]
        '''
        
        # There is a single definition for this word
        maintable = soup.findAll("table", {"class": "maintable"})
        if len(maintable) == 1:
            part_of_speach_row = maintable[0].findAll("tr", {"class": "postitle"})
            likely_class = part_of_speach_row[0].find_all('td', {"class": "data"})[0].a.text
            return [likely_class] if word else likely_class
    
        # Make sure this is not a words suggestion page, if it is return None
        foobar = soup.findAll("div", {"class": "list_title"})
        if len(foobar) == 1 and 'text' in foobar[0] and foobar[0].text.strip() == "Did you mean this word?":
            return None

        # This is a page to pick between multiple definitions
        wordlist = soup.findAll("div", {"class": "wordlist"})
        if len(wordlist) == 1 and 'table' in wordlist[0]:
            ref_links = wordlist[0].table.tbody.findAll("a")
            return [fetchLikelyClass(rid_url = ref['href']) for ref in ref_links]
        
        # No definition found
        return None

    def getLikelyClass(self, word, convert = True, save = True):
        if word in self.words:
            return self.words[word]
        
        rawClassList = self.fetchLikelyClass(word)
        classList = list(set(rawClassList))
        
        if convert or save:
            newClassList = []
            for classItem in classList:
                if classItem in self.parts_of_speach:
                    newClassList.append(self.parts_of_speach[classItem])
            classList = newClassList
            
        if save and classList is not None:
            self.words[word] = classList
        return classList

    def defineLikelyClass(self, word, wordClass, force=False):
        if word not in self.words or force:
            self.words[word] = wordClass
            return True
        return False
