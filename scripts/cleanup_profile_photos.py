"""Run from the repository root: python -m scripts.cleanup_profile_photos."""
from backend.app.core.database import db_manager
from backend.app.profiles.photos import drain_cleanup

if __name__ == '__main__':
    with db_manager.get_connection() as db:
        print(f'Removed {drain_cleanup(db)} queued private objects.')
