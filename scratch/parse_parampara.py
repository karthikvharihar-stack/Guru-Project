import re
import json

file_path = r'C:\Users\Karthik V Harihar\.gemini\antigravity\brain\13896bcb-e323-4b58-bd6f-09b472289b16\.system_generated\steps\420\content.md'

with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Pattern matching each guru card
# <a class="group" href="/parampara/sri-madhwacharya">...<img ... src="https://..."/>...<h4>Sri Madhwacharya</h4>
blocks = re.findall(r'<a class="group" href="/parampara/([^"]+)">([\s\S]*?)</a>', html)

gurus = []
for i, (slug, inner) in enumerate(blocks, 1):
    img_match = re.search(r'src="(https://cdn\.umath\.in/um-assets/parampara/images/[^"]+)"', inner)
    name_match = re.search(r'<h4[^>]*>([^<]+)</h4>', inner)
    
    img_url = img_match.group(1) if img_match else f"https://cdn.umath.in/um-assets/parampara/images/{i-1}.jpg"
    name = name_match.group(1).strip() if name_match else slug.replace('-', ' ').title()
    
    gurus.append({
        'order': i,
        'name': name,
        'slug': slug,
        'image_url': img_url
    })

print(f"Total Gurus extracted: {len(gurus)}")
for g in gurus:
    print(f"#{g['order']:02d}: {g['name']} -> {g['image_url']}")

with open('official_gurus.json', 'w', encoding='utf-8') as f:
    json.dump(gurus, f, indent=2, ensure_ascii=False)
