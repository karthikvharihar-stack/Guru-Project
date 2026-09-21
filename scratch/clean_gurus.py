import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models.guru import Guru

app = create_app('development')
with app.app_context():
    all_gurus = Guru.query.order_by(Guru.guru_order.asc()).all()
    print(f"Total Gurus currently in DB: {len(all_gurus)}")
    for g in all_gurus:
        if '[PLACEHOLDER' in g.name:
            print(f"Deleting placeholder: #{g.guru_order} {g.name}")
            db.session.delete(g)
    db.session.commit()
    
    remaining = Guru.query.order_by(Guru.guru_order.asc()).all()
    print(f"Remaining exact Gurus in DB: {len(remaining)}")
    for r in remaining:
        print(f"#{r.guru_order:02d}: {r.name} ({r.slug})")
