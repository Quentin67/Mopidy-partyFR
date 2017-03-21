from __future__ import absolute_import, unicode_literals

import os

import tornado.web

from mopidy import config, ext

__version__ = '0.2.0'


class PartyRequestHandler(tornado.web.RequestHandler):

    def initialize(self, core, data, config):
        self.core = core
        self.dataPositif = dataPositif
       # self.requiredVotes = config["party"]["votes_to_skip"]
        self.requiredVotes = 3        
    
    def get(self):
        currentTrack = self.core.playback.get_current_track().get()
        if (currentTrack == None): return
        currentTrackURI = currentTrack.uri

        # If the current track is different to the one stored, clear votes
        if (currentTrackURI != self.dataPositif["track"]):
            self.dataPositif["track"] = currentTrackURI
            self.dataPositif["votes_positifs"] = []

        if (self.request.remote_ip in self.dataPositif["votes_positifs"]): # L'utilisateur a deja vote
            self.write("Vous avez deja vote pour passer cette chanson !")
        else: # le vote est valide
            self.dataPositif["votes_positifs"].append(self.request.remote_ip)
            if (len(self.dataPositif["votes_positifs"]) == self.requiredVotes):
                self.core.playback.next()
                self.write("Changement de musique...")
            else:
                self.write("Vous avez vote pour passer cette musique.")



def party_factory(config, core):
    dataPositif = {'track':"", 'votes_positifs':[]}
    return [
    ('/vote_positif', PartyRequestHandler, {'core': core, 'data':data, 'config':config})
    ]


class Extension(ext.Extension):

    dist_name = 'Mopidy-Party'
    ext_name = 'party'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['votes_to_skip'] = config.Integer(minimum=0)
        return schema

    def setup(self, registry):
        registry.add('http:static', {
            'name': self.ext_name,
            'path': os.path.join(os.path.dirname(__file__), 'static'),
        })
        registry.add('http:app', {
            'name': self.ext_name,
            'factory': party_factory,
        })
