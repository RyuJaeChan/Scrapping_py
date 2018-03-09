import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')

from bs4 import BeautifulSoup
import urllib.request as req
from urllib.parse import urljoin
import re
from konlpy.tag import Twitter
from gensim.models import word2vec
from datetime import datetime

time_stamp = datetime.today().strftime("%Y%m%d_%H%M%S")

#sid2 attributes
article_type = { 
    "모바일":"731",
    "인터넷/SNS":"226",
    "통신/뉴미디어":"227",
    "IT 일반":"230",
    "보안/해킹":"732",
    "컴퓨터":"283",
    "게임/리뷰":"229",
    "과학 일반":"228"
 }



## get_article_list
#
def get_article_list(url):
    res = req.urlopen(url)
    soup = BeautifulSoup(res, "html.parser")

    get_links_from_page(url)

    for element in soup.select("#main_content > div.paging > a") :
        if element.string == "다음" :
            get_article_list(urljoin(url, element.attrs['href']))
        elif element.string != "이전" :
            get_links_from_page(urljoin(url, element.attrs['href']))
            
    return 0


## get_page
#
# $ input
#   - type_num   ... string
#       283     : 컴퓨터
#       732     : 보안/해킹
#   - date       ... string
#       yyyymmdd format
# $ output
#   - none
def get_data(type_num, date):
    print('data : ', date)
    #http://news.naver.com/main/list.nhn?mode=LS2D&mid=shm&sid1=105&sid2=283&date=...
    # - sid1=105 : IT/과학 페이지                  뉴스 대분류
    # - sid2=... : 모바일, 인터넷/SNS ...          카테고리 소분류
    main_url = "http://news.naver.com/main/list.nhn"
    route = "?mode=LS2D&mid=shm&sid1=105&sid2="+str(type_num)+"&date=" + str(date)
    url = main_url + route

    print(url)
    get_article_list(url)

    return 0

## get_links_from_page
# $ This function gets article links in specific page
# $ input 
#   - data : url string   ... string
# $ output
#   - none
def get_links_from_page(link):
    res = req.urlopen(link)
    soup = BeautifulSoup(res, "html.parser")
    links_list = soup.select("#main_content > div.list_body.newsflash_body > ul > li > dl > dt:nth-of-type(1) > a[href]")
    for link in links_list :
        print('link : ',link.attrs['href'])
        get_data_from_article(link.attrs['href'])

def clean_text(content):
    #cleaned_text = re.sub('[a-zA-Z]', '', text)
    #cleaned_text = re.sub('[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]',
    #                      '', cleaned_text)
    output = ""
    for item in content.contents:
        stripped = str(item).strip()
        if stripped == "":
            continue
        if stripped[0] not in ["<", "/"]:
            output += str(item).strip()
    output = output.replace("본문 내용TV플레이어","")
    return output


def convert_text2data(text):
    tw = Twitter()
    results = []
    malist = tw.pos(text, norm = True, stem = True)
    r = []
    for word in malist:
        if not word[1] in ["Josa", "Eomi", "Punctuation"]:
        #if word[1] == "Noun":
            r.append(word[0])
            #print(word[0], " ", word[1])
        
    rl = (" ".join(r)).strip()
    results.append(rl)
    #print('result : ', results)
    #print(rl)


    with open(time_stamp + "_wataki.wakati", 'a', encoding='utf-8') as fp:
        fp.write("\n".join(results))


def make_model_file(result_file_name):
    data = word2vec.LineSentence(time_stamp + "_wataki.wakati")
    model = word2vec.Word2Vec(data, size=200, window=10, hs=1, min_count=20, sg=1)
    model.save(result_file_name)
    return 0



##get_data_from_article
# $ This function save article's content from link
# $ input
#   - data : link : url string    ... article's url
# $ output
#   - none
def get_data_from_article(link):
    res = req.urlopen(link)
    soup = BeautifulSoup(res, "html.parser")
    try :
        convert_text2data(clean_text(soup.select_one("#articleBodyContents")))
    except Exception as err:
        print(str(err))
        with open(time_stamp + "_error_log.txt", 'a', encoding='utf-8') as fp:
            fp.write(str(err) + "\n")
            fp.write("link : " + link)


    #for element in soup.select("#articleBodyContents") :
        #print('ele : ' , element.find_all(text=True))
        #convert_text2data(str(element.find_all(text=True)))

    return 0

def make_model(type_num, date):
    
    get_data(type_num, date)   
    #make_model_file(time_stamp + type_num + "_result.model")
    
    return 0

def main():
    date = [
        "20180305", 
        "20180304", 
        "20180303", 
        "20180302", 
        "20180301", 
        "20180228", 
        "20180227", 
        "20180226", 
    ]
    
    for type_num in article_type.values() :
        for day in date :
            print("day : ", day, "  num : ", type_num)
            make_model(type_num, day)
    # make_model_file(time_stamp + "_result.model")
    #get_data_from_article("http://news.naver.com/main/read.nhn?mode=LS2D&mid=shm&sid1=105&sid2=230&oid=277&aid=0004190290")   
    #get_article_list("http://news.naver.com/main/list.nhn?mode=LS2D&sid2=230&sid1=105&mid=shm&date=20180228")

    return 0


if __name__ == '__main__':
    main()
    


    