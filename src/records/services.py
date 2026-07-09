import os
import re
from typing import Dict, Annotated

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlmodel import select

from src.commons import settings
from src.config.dependencies import ProfileDep
from src.database.database import CacheSessionDep
from src.records.models import Record
from src.xslt import RecordMetadataDep, RecordMetadata


class RecordManager:
    """
    Deals with retrieving/saving records and their cache.
    """
    metadata_processor: RecordMetadata
    cache: Session
    records_location: str
    profile: Dict

    def __init__(self, metadata_processor: RecordMetadata, cache: CacheSessionDep,
                 records_location: str, profile: ProfileDep):
        """
        Initialize the record manager
        :param metadata_processor:
        :param cache:
        """
        self.metadata_processor = metadata_processor
        self.cache = cache
        self.records_location = records_location
        self.profile = profile


    def build_cache(self):
        """
        Clear cache. Iterate over all records and store them in the cache db.
        :return:
        """
        # First clear the records table
        self.cache.query(Record).delete()
        self.cache.commit()


        filenames = (
            re.match(r"^record-(.*)\.xml$", f) for f in os.listdir(self.records_location)
        )
        records = (
            m.group(1) for m in filenames if m is not None
        )

        for r in records:
            metadata = self.get_metadata(r)
            record = Record(id=r, fields=metadata)
            self.cache.add(record)
        self.cache.commit()

    def get_metadata(self, record_id: str | int) -> Dict:
        """
        Get metadata for a single record
        :param record_id:
        :return:
        """
        self.metadata_processor.set_record(record_id)

        fixed_props = {
            "owner": {
                "xpath": "(/*:CMD/*:Header/*:MdCreator,'server')[1]"
            },
            "creationDate": {
                "xpath": "/*:CMD/*:Header/*:MdCreationDate"
            }
        }
        custom_props = self.profile["list"]
        combined = {**custom_props, **fixed_props}

        tmp = {}
        for key, value in combined.items():
            tmp[key] = self.metadata_processor.parse_single(value['xpath'])
        return tmp

    def add_record(self, record_id: int | str):
        """
        Add a new record to the cache
        :param record_id:
        :return:
        """
        record = Record(id=record_id, fields=self.get_metadata(record_id))
        self.cache.add(record)
        self.cache.commit()

    def update_record(self, record_id: int | str):
        """
        Update a record in the cache
        :param record_id:
        :return:
        """
        record: Record = self.cache.scalars(select(Record).where(Record.id == record_id)).first()
        record.fields = self.get_metadata(record_id)
        self.cache.commit()

    def delete_record(self, record_id: int | str):
        """
        Delete a record from the cache
        :param record_id:
        :return:
        """
        record: Record = self.cache.scalars(select(Record).where(Record.id == record_id)).first()
        self.cache.delete(record)
        self.cache.commit()

    def list(self, start: int = 0, limit: int = 100):
        records = self.cache.scalars(select(Record).offset(start).limit(limit))
        return records.all()


    def num_records(self) -> int:
        """
        Get the total number of records
        :return:
        """
        return self.cache.query(Record).count()


def get_record_manager(app: str, metadata_processor: RecordMetadataDep, cache: CacheSessionDep,
                       profile: ProfileDep) -> RecordManager:
    record_dir = f"{settings.URL_DATA_APPS}/{app}/profiles/{profile['prof']}/records"
    return RecordManager(metadata_processor, cache, record_dir, profile)

RecordManagerDep = Annotated[RecordManager, Depends(get_record_manager)]