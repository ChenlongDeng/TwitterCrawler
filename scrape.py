import json
import requests
from tqdm import tqdm

username = 'Beijing2022' # 填写你要搜索的用户名称
since_date = '2014-01-01' # 填写筛选推文的开始时间
until_date = '2022-03-01' # 填写筛选推文的结束时间
tweets = []
max_tweetnum = 100 # 填写爬取的推文最大数量
first_scroll = True

params = {
    'tweet_mode': 'extended',
    'tweet_search_mode': 'live',
    'query_source': 'typd',
    'include_quote_count': 'true',
    'include_reply_count': 1,
    'q': f'from:{username}+since:{since_date}+until:{until_date}',
    'cursor': None,
}

headers = {
    # 填写示例图片中参数位置
    'authorization': '',
    'x-guest-token': '',
}

tweet_iterator = tqdm(range(max_tweetnum), ncols=120)


while len(tweets) < max_tweetnum:
    tweet_data = requests.get('https://twitter.com/i/api/2/search/adaptive.json', headers=headers, params=params).json()
    
    update_num = 0
    for tweet in tweet_data['globalObjects']['tweets']:
        subkey = ['id', 'created_at', 'full_text', 'retweet_count', 'favorite_count', 'reply_count', 'quote_count']
        tweets.append({key:tweet_data['globalObjects']['tweets'][tweet][key] for key in subkey})
        update_num += 1
    
    if first_scroll:
        entries = tweet_data['timeline']['instructions'][0]['addEntries']['entries']
        for entry in entries:
            if entry['entryId'] == 'sq-cursor-bottom':
                params['cursor'] = entry['content']['operation']['cursor']['value']
        first_scroll = False
    else:
        for instruction in tweet_data['timeline']['instructions']:
            if 'replaceEntry' in instruction:
                if instruction['replaceEntry']['entryIdToReplace'] == 'sq-cursor-bottom':
                    params['cursor'] = instruction['replaceEntry']['entry']['content']['operation']['cursor']['value']
    
    if len(tweets) <= max_tweetnum:
        tweet_iterator.update(update_num)
    else:
        tweet_iterator.update(max_tweetnum - tweet_iterator.last_print_n)

tweet_iterator.close()
with open('./results.json', 'w') as f:
    json.dump(tweets, f)
print('Total number of tweets crawled: {}'.format(len(tweets)))

