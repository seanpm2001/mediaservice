#!/usr/bin/env python
import re

import cream.ipc
import cream.extensions

from crawler import crawl

def mongodb_to_dbus_dict(dict_):
    dict_['_id'] = unicode(dict_['_id'])
    return dict_

@cream.extensions.register
class AudioExtension(cream.extensions.Extension, cream.ipc.Object):

    __ipc_signals__ = {
        'library_updated': ('', 'org.cream.Mediaservice.Audio')
    }

    def __init__(self, extension_interface):
        cream.extensions.Extension.__init__(self, extension_interface)
        cream.ipc.Object.__init__(self,
            'org.cream.mediaservice',
            '/org/cream/Mediaservice/Audio'
        )
        self.collection = extension_interface.database.audio


    @cream.ipc.method('s')
    def update_library(self, path):
        crawl(self.collection.tracks, path)
        self.emit_signal('library_updated')

    @cream.ipc.method('a{sv}b', 'aa{sv}', interface='org.cream.Mediaservice.Audio')
    def query(self, query, ignorecase):
        if ignorecase:
            for key, value in query.iteritems():
                if isinstance(value, basestring):
                    query[key] = re.compile(value, re.IGNORECASE)

        return map(mongodb_to_dbus_dict, self.collection.tracks.find(query))

    @cream.ipc.method('sa{sv}', '', interface='org.cream.Mediaservice.Audio')
    def update_track(self, _id, track_new):
        self.collection.update({'_id': _id}, {'$set': track_new})

    @cream.ipc.method('s', '', interface='org.cream.Mediaservice.Audio')
    def remove_track(self, _id):
        self.collection.remove(_id)
