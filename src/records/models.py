from typing import Any, Dict, Optional

from sqlalchemy.orm import mapped_column, Mapped

from src.auth.models import User
from src.database.models import CacheBase
from src.xslt import RecordMetadata


class Record(CacheBase):
    """
    Record model
    """
    __tablename__ = "records"

    id: Mapped[int] = mapped_column(primary_key=True)
    fields: Mapped[dict[str, Any]]
    profile: Mapped[str] = mapped_column(index=True)

    def table_data(self, user: Optional[User], config: Dict, record_metadata: RecordMetadata):
        """
        Return data to display in table
        :return:
        """
        permissions = config["app"]["access"]
        username = user.name if user else None

        def allowed(permission: str) -> bool:
            if permissions[permission] in ['users', 'any']:
                return True
            elif permissions[permission] == 'owner':
                return self.fields["owner"] == username
            return False


        return {
            "_id": self.id,
            **self.fields,
            "read": allowed("read"),
            "write": allowed("write"),
        }