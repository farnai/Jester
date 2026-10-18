"""Run destructive legacy tests against a disposable DB clone on local Supabase.

The Storage HTTP integration suite runs separately against its UUID-only fixtures.
No dump/credentials are written to repository files.
"""
import os
import subprocess
import uuid
from urllib.parse import urlsplit, urlunsplit

import psycopg
from psycopg import sql
from backend.app.config import get_settings

settings = get_settings()
original_url = settings.DATABASE_URL
parsed = urlsplit(original_url)
if settings.ENV == 'production' or parsed.hostname not in ('127.0.0.1', 'localhost'):
    raise RuntimeError('Isolated regression is local only')
name = 'qa_wave2_' + uuid.uuid4().hex
isolated_url = urlunsplit(parsed._replace(path='/' + name))
real_connect = psycopg.connect
with psycopg.connect(original_url, autocommit=True) as admin:
    admin.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
try:
    dump = subprocess.run(['docker', 'exec', 'supabase_db_Jester', 'pg_dump', '-U', 'postgres', '-Fc', '-d', parsed.path[1:]], capture_output=True, check=True)
    restore = subprocess.run(['docker', 'exec', '-i', 'supabase_db_Jester', 'pg_restore', '-U', 'supabase_admin', '-d', name], input=dump.stdout, capture_output=True)
    if restore.returncode:
        for line in restore.stderr.decode(errors='replace').splitlines():
            if 'ERROR:' in line:
                print(line.split('ERROR:', 1)[1])
        raise RuntimeError('Disposable DB restore failed; no tests executed')
    os.environ['DATABASE_URL'] = isolated_url
    get_settings.cache_clear()
    from backend.app.core.database import db_manager
    db_manager.settings = get_settings()
    import tests.database.test_database_security as security
    import tests.backend.test_phase1_foundation as foundation
    security.DB_URL = isolated_url
    foundation.DB_URL = isolated_url
    # Redirect legacy hardcoded URLs as well as configured backend connections.
    def isolated_connect(conninfo='', *args, **kwargs):
        if conninfo == original_url:
            conninfo = isolated_url
        return real_connect(conninfo, *args, **kwargs)
    psycopg.connect = isolated_connect
    import pytest
    code = pytest.main(['tests', '--ignore=tests/backend/test_social_profiles.py', '--ignore=tests/backend/test_discovery_deck.py', '-q', '--tb=short'])
    psycopg.connect = real_connect
finally:
    psycopg.connect = real_connect
    # This name is generated above; never drop the user's postgres database.
    with psycopg.connect(original_url, autocommit=True) as admin:
        admin.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(name)))
raise SystemExit(code)
