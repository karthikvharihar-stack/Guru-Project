import requests

# Test homepage
r_home = requests.get('http://127.0.0.1:5000/')
print('Homepage status:', r_home.status_code)
print('Navbar brand present on homepage:', 'class="navbar-brand"' in r_home.text)
print('Official emblem in hero on homepage:', 'official-emblem-container' in r_home.text)

# Test subpage
r_guru = requests.get('http://127.0.0.1:5000/guru/')
print('Guru page status:', r_guru.status_code)
print('Navbar brand present on /guru/:', 'class="navbar-brand"' in r_guru.text)
