from sqlalchemy.orm import Session

from src.auth.authentication import initialize_users
from src.config.dependencies import get_all_apps, get_app_configuration
from src.database.database import get_db_eng_for_app, get_cache_eng_for_app
from src.database.models import Base, CacheBase
from src.records.services import get_record_manager
from src.xslt import get_metadata_processor, get_saxon_processor

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

        with Session(cache) as session:
            print("Initializing records cache")
            profiles = config["app"]["prof"].values()
            for profile in profiles:
                processor = get_metadata_processor(a, profile, next(get_saxon_processor()))
                manager = get_record_manager(a, processor, session, profile)
                print(f"Building cache for profile {profile['prof']}")
                manager.build_cache()

    print("Finished startup")