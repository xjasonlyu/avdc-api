from peewee import *
from playhouse.db_url import connect

db_proxy = DatabaseProxy()


def database_init(url: str):
    db = connect(url,
                 field_types={'ARRAY': 'TEXT'})
    db_proxy.initialize(db)
    # create table if not exist
    db_proxy.create_tables([Metadata, Actresses, Covers])


class ArrayField(Field):
    field_type = 'ARRAY'

    def db_value(self, value: list[str]) -> str:
        return ','.join(v for v in value) if value else ''

    def python_value(self, value: str) -> list[str]:
        return value.split(',') if value else []


class BasicModel(Model):
    class Meta:
        database = db_proxy


class Metadata(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    title = TextField()

    # cast fields
    director = TextField()
    actresses = ArrayField()

    # info fields
    overview = TextField()
    genres = ArrayField()
    label = TextField()
    studio = TextField()
    series = TextField()
    runtime = IntegerField()

    # image fields
    cover = TextField()
    images = ArrayField()

    # date fields
    release = DateField()

    # source fields
    providers = ArrayField()
    sources = ArrayField()


class Actresses(BasicModel):
    name = CharField(primary_key=True, unique=True)
    images = ArrayField()

    # nullable fields
    measurements = TextField(null=True)
    cup_size = TextField(null=True)
    blood_type = TextField(null=True)
    height = TextField(null=True)
    nationality = TextField(null=True)
    av_activity = DateField(null=True)
    birthday = DateField(null=True)

    # source fields
    providers = ArrayField(null=True)
    sources = ArrayField(null=True)


class Covers(BasicModel):
    vid = CharField(primary_key=True, unique=True)
    width = IntegerField()
    height = IntegerField
    format = CharField()
    pos = DoubleField(default=-1)
    data = BlobField()


if __name__ == '__main__':
    database_init('sqlite:///:memory:')
