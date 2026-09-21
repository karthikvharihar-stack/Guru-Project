import requests
for i in [0, 1, 5, 14, 41]:
    url = f'https://cdn.umath.in/um-assets/parampara/images/{i}.jpg'
    try:
        r = requests.head(url, timeout=5)
        print(f"Image {i}: status {r.status_code}")
    except Exception as e:
        print(f"Image {i}: error {e}")
