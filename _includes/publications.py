import json
import requests

url = 'https://api.zotero.org/users/4797004/publications/items?linkwrap=1&order=date&sort=desc&start=0&include=data&limit=100&style='

resp = requests.get(url=url)
data = resp.json()

sorted(data, key=lambda k: k['meta']['parsedDate'])
with open('publications.html', 'w') as f:
	for p in data:
		if 'proceedingsTitle' in p['data']:
			authors = ", ".join('{0} {1}'.format(a['firstName'], a['lastName']) for a in p['data']['creators']).replace('Bertil Chapuis', '<b>Bertil Chapuis</b>')
			title = p['data']['title']
			proceedings = p['data']['proceedingsTitle']
			pages = p['data']['pages']
			doi = p['data']['DOI']
			date = p['meta']['parsedDate']

			print(f'<li>{authors}. <a href="https://doi.org/{doi}"><b>{title}</b></a>. {proceedings}, {pages}.</li>', file=f)
