from sqlalchemy.orm import Session

from src.auth.authentication import initialize_users
from src.config.dependencies import get_all_apps, get_app_configuration
from src.database.database import get_db_eng_for_app, get_cache_eng_for_app
from src.database.models import Base, CacheBase

if __name__ == "__main__":

    print("Running startup script")
    print("Available apps:")

    for a in get_all_apps():
        print(f" - {a}")
        eng = get_db_eng_for_app(a)
        cache = get_cache_eng_for_app(a)
        config = get_app_configuration(a)
        Base.metadata.create_all(eng)
        CacheBase.metadata.create_all(cache)

        with Session(eng) as session:
            print("Check if this app has users")
            initialize_users(a, config, session)

    print("Finished startup")