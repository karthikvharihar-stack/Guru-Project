import requests
import re

r = requests.get('http://127.0.0.1:5000/guru/')
cards = re.findall(r'class="guru-foiled-card[^"]*"', r.text)
print(f"Total rendered Guru cards in /guru/: {len(cards)}")
assert len(cards) == 42, f"Expected 42, got {len(cards)}"
print("ALL 42 OFFICIAL GURUS ARE RENDERED ON /guru/!")
