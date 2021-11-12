import urllib.request
import json
import time
from rank_mapper import build_rank_dict, get_rank


def fetch_dblp(topic, hit_count):
    url = "https://dblp.org/search/publ/api"
    params = {
        "q": topic,
        "h": hit_count,
        "format": "json"
    }
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as url_:
        data = json.loads(url_.read().decode())
        # get relevant data
        paper_list = list()
        # check if key 'hit' exists in data['result']['hits']
        if 'hit' not in data['result']['hits']:
            return paper_list
        for entry in data['result']['hits']['hit']:
            paper_info = {}
            if entry['info']['type'] == 'Conference and Workshop Papers':
                paper_info['title'] = entry['info']['title']
                author_lst = list()
                auths = entry['info']['authors']['author']
                if isinstance(auths, dict):
                    author_lst.append(auths['text'])
                else:
                    for a in auths:
                        author_lst.append(a['text'])
                paper_info['authors'] = author_lst
                paper_info['venue'] = entry['info']['venue']
                paper_info['year'] = entry['info']['year']
                paper_info['url'] = entry['info']['url']
                paper_info['rank'] = get_rank(
                    paper_info['venue'].split()[0].lower())
                paper_list.append(paper_info)
        # write to file
        # open(topic, 'w').write(json.dumps(paper_list))
        return paper_list


# build_rank_dict('ranks1.json')
# build_rank_dict('ranks2.json')

# while True:
#     topic = input("Enter topic: ")
#     hit_count = int(input("Enter hit count: "))
#     if topic == "exit" or hit_count == 0:
#         break
#     else:
#         start = time.time()
#         paper_list = fetch_dblp(topic, hit_count)
#         for paper in paper_list:
#             # print(paper)
#             print(json.dumps(paper, indent=4))
#         print(len(paper_list))
#         print("Time taken: ", time.time() - start)
#         # print("-"*100)
