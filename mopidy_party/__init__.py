from __future__ import absolute_import, unicode_literals

import os

import tornado.web

from mopidy import config, ext

__version__ = '0.2.0'


class PartyRequestHandler(tornado.web.RequestHandler):

    def initialize(self, core, data, config):
        self.core = core
        self.data = data
       # self.requiredVotes = config["party"]["votes_to_skip"]
        #self.requiredVotes = 3        
        self.dejaVote = 0
        
    def get(self):
        currentTrack = self.core.playback.get_current_track().get()
        if (currentTrack == None): return
        currentTrackURI = currentTrack.uri

        # If the current track is different to the one stored, clear votes
        if (currentTrackURI != self.data["track"]):
            self.data["track"] = currentTrackURI
            self.data["votes_positif"] = []
            self.data["votes_negatif"] = []

    if (self.request.remote_ip in self.data["votes_positif"]):  #on verifie si l'utilisateur a deja fait un vote positif
        self.dejaVote = 1
        
    if (self.request.remote_ip in self.data["votes_negatif"]): #on verifie si l'utilisateur a deja fait un vote negatif
        self.dejaVote = 1
        
    if (self.dejaVote == 1): # L'utilisateur a deja vote
            self.write("Vous avez deja vote pour passer cette chanson !")
    else: # le vote est valide
            self.data["votes_positif"].append(self.request.remote_ip)
            self.data["votes_negatif"].append(self.request.remote_ip)
            if ((len(self.data["votes_positif"]- len(self.data["votes_negatif"])) == 0):
                self.core.playback.next()
                self.write("Changement de musique...")
            else:
                self.write("Vous avez vote pour passer cette musique")



def party_factory(config, core):
    data = {'track':"", 'votes_positif', 'votes_negatif':[]}
    return [
    ('/votes_negatif', PartyRequestHandler, {'core': core, 'data':data, 'config':config})
    ('/votes-positif', PartyRequestHandler, {'core': core, 'data': data, 'config': config})
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
