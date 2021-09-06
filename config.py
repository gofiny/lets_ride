import os
import sys


try:
    _db_user = os.environ["DB_USER"]
    _db_password = os.environ["DB_PASSWORD"]
    _db_database = os.environ["DB_DATABASE"]
except KeyError as key:
    print(f"Var {key} doesn't exist")
    sys.exit()

DB_DESTINATION = f"postgres://{_db_user}:{_db_password}@localhost/{_db_database}"
