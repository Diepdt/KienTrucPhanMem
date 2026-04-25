import urllib.request, json

def chat(msg):
    data = json.dumps({'customer_id': 0, 'message': msg}).encode()
    url = 'http://recommender-ai-service:8011/api/chat/'
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    resp = urllib.request.urlopen(req)
    r = json.loads(resp.read().decode())
    rp = r['reply']
    print('Q:', msg)
    print('A:', rp[:220])
    print('   products:', len(r.get('recommended_products', [])))
    print()

chat('xin chao')
chat('An lac tung buoc chan')
chat('sach tam linh')
chat('san pham duoi 200k')
chat('laptop')
chat('re nhat')
chat('sach hay')
chat('hao hao chua cay')
