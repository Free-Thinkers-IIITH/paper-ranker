import json
conf_rank = dict()

def build_rank_dict(file_name):
    with open(file_name) as f:
        for conf in json.load(f):
            conf_rank[conf['Acronym'].lower()] = conf['Rank']
def get_rank(conf_name):
    if conf_name in conf_rank:
        return conf_rank[conf_name]
    else:
        return None

# build_rank_dict('ranks1.json')
# build_rank_dict('ranks2.json')

# for conf in conf_rank:
#     print(conf, conf_rank[conf])
