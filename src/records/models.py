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

    def table_data(self, user: Optional[User], config: Dict, record_metadata: RecordMetadata):
        """
        Return data to display in table
        :return:
        """
        permissions = config["app"]["access"]
        username = user.name if user else None

        actions = config["app"]["hooks"]["action"]
        actions_enabled = {}
        xpath_initialized = False
        for name, action in actions.items():
            if "enable" not in action:
                actions_enabled[name] = True
                continue
            if not xpath_initialized:
                xpath_initialized = True
                record_metadata.set_record(self.id)
                record_metadata.set_parameter("self", f"unl://{self.id}")
            try:
                actions_enabled[name] = record_metadata.parse_single(action["enable"]) == "true"
            except Exception as e:
                actions_enabled[name] = False
                print(f"Error when evaluating 'enabled' status of action {name}")
                print(e)

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
            "actionsEnabled": actions_enabled,
        }