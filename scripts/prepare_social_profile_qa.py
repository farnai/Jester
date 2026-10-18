"""Create isolated, explicitly labeled local QA accounts; never alter real users.

Credentials are random and written only to ignored scratch/. Run from repo root.
"""
import json
import secrets
import sys
import uuid
from pathlib import Path
import httpx
from backend.app.core.database import db_manager
from backend.app.profiles.photos import drain_cleanup

settings = db_manager.settings
if settings.ENV == 'production' or '127.0.0.1' not in settings.SUPABASE_URL:
    raise RuntimeError('Local development only')
manifest = Path('scratch/wave2-accounts.json')
if '--cleanup' in sys.argv:
    for account in json.loads(manifest.read_text(encoding='utf-8')):
        response = httpx.get(settings.SUPABASE_URL + '/auth/v1/admin/users/' + account['id'], headers=db_manager.get_admin_headers())
        response.raise_for_status()
        if response.json()['email'] != account['email'] or not account['email'].startswith('wave2-browser-'):
            raise RuntimeError('Refusing to remove an account outside the QA manifest')
        httpx.delete(settings.SUPABASE_URL + '/auth/v1/admin/users/' + account['id'], headers=db_manager.get_admin_headers()).raise_for_status()
    with db_manager.get_connection() as db:
        drain_cleanup(db)
    manifest.unlink()
    print('Removed only the two manifest-verified QA accounts and their private media.')
    raise SystemExit(0)
accounts = []
for index in range(2):
    email = f'wave2-browser-{uuid.uuid4()}@example.invalid'
    password = secrets.token_urlsafe(24)
    r = httpx.post(settings.SUPABASE_URL + '/auth/v1/admin/users', headers=db_manager.get_admin_headers(),
                   json={'email': email, 'password': password, 'email_confirm': True})
    r.raise_for_status()
    uid = r.json()['id']
    token = httpx.post(settings.SUPABASE_URL + '/auth/v1/token?grant_type=password',
                      headers={'apikey': settings.SUPABASE_ANON_KEY}, json={'email': email, 'password': password})
    token.raise_for_status()
    with httpx.Client(base_url='http://127.0.0.1:8000', headers={'Authorization': 'Bearer ' + token.json()['access_token']}) as ac:
        ac.post('/v1/profiles/initialize').raise_for_status()
        with db_manager.get_connection() as db:
            city = db.execute("SELECT id FROM public.cities WHERE name_ascii = 'Tbilisi' LIMIT 1").fetchone()['id']
            db.execute("INSERT INTO public.birth_data(user_id,birth_date,birth_time_precision,birth_timezone,birth_city_id) VALUES(%s,'1995-05-15','unknown','Asia/Tbilisi',%s)", (uid,city))
        ac.patch('/v1/profiles/me', json={'first_name': 'ანა' if index == 0 else 'ნიკა', 'last_name': 'ტესტი',
            'display_name': 'ანა · სატესტო პროფილი' if index == 0 else 'ნიკა · სატესტო პროფილი',
            'current_city_id': str(city), 'occupation': 'დიზაინი და ფოტოგრაფია',
            'bio': 'ლოკალური QA პროფილი · დემო ფოტოები. მიყვარს ქალაქში ხეტიალი, ახალი ადგილების აღმოჩენა და გრძელი საუბრები ხელოვნებაზე.'}).raise_for_status()
        ac.post('/v1/profiles/me/complete-onboarding').raise_for_status()
        ac.post('/v1/astrology/profile/recalculate').raise_for_status()
        interests = [i['id'] for i in ac.get('/v1/interests').json()['items']]
        ac.put('/v1/interests/me', json={'interest_ids': interests[index:index+4]}).raise_for_status()
    accounts.append({'id': uid, 'email': email, 'password': password})
manifest.write_text(json.dumps(accounts), encoding='utf-8')
print('Created two labeled local QA accounts; credentials saved in ignored scratch file.')
