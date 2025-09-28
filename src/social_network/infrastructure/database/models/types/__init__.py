import datetime
import uuid

import sqlalchemy

type_annotation_mapper = {
    str: sqlalchemy.VARCHAR(256),
    datetime.datetime: sqlalchemy.DateTime(timezone=True),
    uuid.UUID: sqlalchemy.UUID,
}
