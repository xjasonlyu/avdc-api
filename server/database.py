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
        return ','.join(value)

    def python_value(self, value: str) -> list[str]:
        return value.split(',')


class BasicModel(Model):
    class Meta:
        database = sqlite_db


class Metadata(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    title = TextField()

    # info fields
    overview = TextField(null=True)
    tags = ArrayField(null=True)
    label = TextField(null=True)
    studio = TextField(null=True)
    series = TextField(null=True)
    runtime = IntegerField(null=True)

    # cast fields
    stars = ArrayField(null=True)
    director = TextField(null=True)

    # image fields
    cover = TextField(null=True)
    small_cover = TextField(null=True)
    images = ArrayField(null=True)

    # source fields
    source = ArrayField(null=True)
    website = ArrayField(null=True)

    # date fields
    release = DateField(null=True)

    # datetime fields
    created = DateTimeField(default=datetime.now)
    updated = DateTimeField(null=True)


class People(BasicModel):
    name = CharField(primary_key=True, unique=True)
    images = ArrayField(null=True)


class Cover(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    format = CharField()
    data = BlobField()


if __name__ == '__main__':
    sqlite_db_init('example.db')
