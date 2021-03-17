from datetime import datetime

from peewee import *

sqlite_db = SqliteDatabase(
    None,
    field_types={'ARRAY': 'TEXT'},
)


def sqlite_db_init(db: str):
    sqlite_db.init(database=db)
    # create table if not exist
    sqlite_db.create_tables([Metadata, People, Cover])


class ArrayField(Field):
    field_type = 'ARRAY'

    def db_value(self, value: list[str]) -> str:
        return ','.join(i.strip() for i in value)

    def python_value(self, value: str) -> list[str]:
        return value.strip().split(',')


class BasicModel(Model):
    class Meta:
        database = sqlite_db


class Metadata(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    title = TextField()

    # info fields
    overview = TextField()
    tags = ArrayField()
    label = TextField()
    studio = TextField()
    series = TextField()
    runtime = IntegerField()

    # cast fields
    stars = ArrayField()
    director = TextField()

    # image fields
    cover = TextField()
    images = ArrayField()

    # source fields
    source = ArrayField()
    website = ArrayField()

    # date fields
    release = DateField()

    # datetime fields
    last_modified = DateTimeField(default=datetime.now)


class People(BasicModel):
    name = CharField(primary_key=True, unique=True)
    images = ArrayField()


class Cover(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    format = CharField()
    data = BlobField()


if __name__ == '__main__':
    sqlite_db_init('example.db')
