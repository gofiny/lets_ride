import os
import sys


try:
    _db_user = os.environ["DB_USER"]
    _db_password = os.environ["DB_PASSWORD"]
    _db_database = os.environ["DB_DATABASE"]
    DOMAIN_NAME = os.environ["DOMAIN_NAME"]
except KeyError as key:
    print(f"Var {key} doesn't exist")
    sys.exit()

DB_DESTINATION = f"postgres://{_db_user}:{_db_password}@localhost/{_db_database}"
PUBLIC_METHODS = {"/registration", "/authorization"}
STATIC_FILES = "static"
