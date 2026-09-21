import requests

r = requests.get('http://127.0.0.1:5000/')
print('Status:', r.status_code)
print('Contains Sri Digvijaya Moola Ramo Vijayate:', 'श्री दिग्विजय मूलरामो विजयते' in r.text)
print('Contains SRI JAGADGURU MADHVACHARYA MOOLA MAHA SAMSTANAM:', 'SRI JAGADGURU MADHVACHARYA MOOLA MAHA SAMSTANAM' in r.text)
print('Emblem logo box removed from hero:', 'official-emblem-container' not in r.text)
print('Hanuman present on left:', 'hanuman_left.png' in r.text)
print('Garuda present on right:', 'garuda_right.png' in r.text)
