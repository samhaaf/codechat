from sqlalchemy import or_
from typing import List, Dict, Optional
from .model import AccessModel


class AccessManager:
    """ Checks access permissions to a table for a given user.
        A new object gets instantiated for each query session.
    """

    def __init__(self, table: str, model: type, user_uid: str):
        self.table = table
        self.model = model
        self.user_uid = user_uid
        self.group_uids = []  # TODO: query for all groups the user belongs to
        self.access_records = self._get_access_records()
        self.comprehensive_conditions = self._build_comprehensive_access_conditions()

    def _get_access_records(self) -> List[AccessModel]:
        return AccessModel.query.filter(
            or_(
                AccessModel.user_uid == self.user_uid,
                AccessModel.group_uid.in_(self.group_uids)
            )
        ).all()

    def _build_comprehensive_access_conditions(self) -> Dict:
        comprehensive_conditions = {}
        for record in self.access_records:
            # Assume each record has a 'conditions' attribute which is a JSON blob
            for field, condition in record.conditions.items():
                if field not in comprehensive_conditions:
                    comprehensive_conditions[field] = []
                comprehensive_conditions[field].append(condition)
        return comprehensive_conditions

    def check_access(self, row_conditions: Dict, can_read: Optional[bool] = None, can_insert: Optional[bool] = None, can_update: Optional[bool] = None, can_delete: Optional[bool] = None) -> bool:
        for field, value in row_conditions.items():
            if field not in self.comprehensive_conditions:
                return False

            permitted_values = self.comprehensive_conditions[field]
            if value not in permitted_values and '*' not in permitted_values:
                return False

        # At this point, row conditions have been satisfied
        return True

    def all_rows_with_access(self, start: int = 0, offset: int = 0, count: int = 10, sort_by: Optional[str] = None,
                             can_read: Optional[bool] = None, can_insert: Optional[bool] = None, can_update: Optional[bool] = None, can_delete: Optional[bool] = None) -> List[Dict]:
        query = self.model.query
        for field, conditions in self.comprehensive_conditions.items():
            query = query.filter(or_(
                getattr(self.model, field).in_(conditions),
                getattr(self.model, field) == '*'
            ))

        # Apply pagination and sorting here
        query = query.offset(start + offset).limit(count)
        if sort_by:
            query = query.order_by(sort_by)

        return query.all()

    def assert_access(self, row_conditions: Dict, can_read: Optional[bool] = None, can_insert: Optional[bool] = None, can_update: Optional[bool] = None, can_delete: Optional[bool] = None):
        if not any(perm is True for perm in [can_read, can_insert, can_update, can_delete]):
            raise RuntimeError('AccessSession.assert_access requires one can_* param to be True. Developer Error.')

        if not self.check_access(row_conditions, can_read, can_insert, can_update, can_delete):
            raise PermissionError(f"{self.user_uid} does not have access to the requested resource.")
