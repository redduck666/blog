import uuid
from datetime import datetime

import tragedy
client = tragedy.connect(['localhost:9160'])

from tragedy import *

from pylons import config


dev_cluster  = Cluster('Dev Cluster')
twitty_keyspace = Keyspace('Keyspace1', dev_cluster)

class Post(Model):
    slug = RowKey()
    title = StringField()
    text = StringField()
    pub_date = TimestampField(autoset_on_create=True)
    tags = ListField(mandatory=False)

    def txt(self):
        text = self.column_value.get('text')
        if isinstance(text, str):
            return unicode(text, errors='ignore')
        else:
            # already unicode
            return text

    def date(self):
        hex_value = self.pub_date.value_to_external(self.column_value['pub_date'])
        ts = timestamp.fromUUID(uuid.UUID(hex=hex_value))
        return datetime.fromtimestamp(ts)

    def url(self):
        date = self.date()
        return '%s/%s/%s/%s/%s/' % (config['blog_base_url'], date.year, date.month, date.day, self.get('slug'))

    def html_tags(self):
        if self.get('tags'):
            return ['<a href="/history/%s/0/">%s</a>' % (i, i) for i in self.get('tags')]
        return []


class Tag(Index):
    name = RowKey()
    targetmodel = ForeignKey(foreign_class=Post, compare_with='BytesType')


