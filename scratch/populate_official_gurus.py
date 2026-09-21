import os
import json
import requests
import sys
sys.path.insert(0, os.path.abspath('.'))

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.guru import Guru, GuruSource, GuruWork

with open('official_gurus.json', 'r', encoding='utf-8') as f:
    gurus_data = json.load(f)

# Create images folder
img_dir = os.path.join('app', 'static', 'images', 'gurus')
os.makedirs(img_dir, exist_ok=True)

print(f"Downloading {len(gurus_data)} official Guru photos...")
for g in gurus_data:
    order = g['order']
    img_filename = f"{order:02d}_{g['slug']}.jpg"
    local_path = os.path.join(img_dir, img_filename)
    web_path = f"/static/images/gurus/{img_filename}"
    
    if not os.path.exists(local_path):
        try:
            r = requests.get(g['image_url'], timeout=10)
            if r.status_code == 200:
                with open(local_path, 'wb') as img_f:
                    img_f.write(r.content)
                g['local_image_url'] = web_path
                print(f"[OK] Downloaded #{order:02d} {g['name']}")
            else:
                g['local_image_url'] = g['image_url']
                print(f"[WARN] Failed #{order:02d}, status {r.status_code}")
        except Exception as e:
            g['local_image_url'] = g['image_url']
            print(f"[ERR] #{order:02d}: {e}")
    else:
        g['local_image_url'] = web_path
        print(f"[EXISTS] #{order:02d} {g['name']}")

# Now update the database
app = create_app('development')
with app.app_context():
    print("\nUpdating database with all 42 official Gurus...")
    
    # Clear existing gurus or update
    existing_gurus = {g.guru_order: g for g in Guru.query.all()}
    created_or_updated = []
    
    for g in gurus_data:
        order = g['order']
        name = g['name']
        slug = g['slug']
        img_url = g.get('local_image_url', g['image_url'])
        
        guru_obj = existing_gurus.get(order)
        if not guru_obj:
            guru_obj = Guru(
                guru_order=order,
                name=name,
                slug=slug,
                image_url=img_url,
                is_verified=True,
                is_active=True
            )
            db.session.add(guru_obj)
        else:
            guru_obj.name = name
            guru_obj.slug = slug
            guru_obj.image_url = img_url
            guru_obj.is_verified = True
            guru_obj.is_active = True
        
        created_or_updated.append(guru_obj)
    
    db.session.commit()
    
    # Now link previous_guru and next_guru in unbroken chain
    for i in range(len(created_or_updated)):
        cur = created_or_updated[i]
        if i > 0:
            cur.previous_guru_id = created_or_updated[i - 1].id
        else:
            cur.previous_guru_id = None
            
        if i < len(created_or_updated) - 1:
            cur.next_guru_id = created_or_updated[i + 1].id
        else:
            cur.next_guru_id = None
            
    db.session.commit()
    print(f"Successfully configured all {len(created_or_updated)} Gurus with unbroken lineage links!")
