"""
JESTER — Database Identity & Schema Verification Utility
Validates that DATABASE_URL points to the authoritative JESTER Supabase PostgreSQL
database with all required migrations, tables, columns, and seed datasets.
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.database import verify_database_identity, DatabaseIdentityError, db_manager


def main():
    print(f"Checking database connection at: {db_manager.settings.DATABASE_URL}...")
    try:
        info = verify_database_identity()
        print("\n" + "=" * 60)
        print("✓ DATABASE VERIFICATION SUCCESSFUL")
        print("=" * 60)
        print(f"Host              : {info['host']}")
        print(f"Port              : {info['port']}")
        print(f"Database          : {info['dbname']}")
        print(f"Migration Version : {info['migration_version']}")
        print(f"Canonical Cities  : {info['city_count']}")
        print("=" * 60)
        print("The database is correctly configured and ready for JESTER.\n")
        return 0
    except DatabaseIdentityError as e:
        print(f"\n{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nUnexpected error during database verification: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
