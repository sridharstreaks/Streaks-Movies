from flask import Flask, jsonify, abort, request
from utils import imdb_retriver
from tamilmv_stremio import Tamilmv
from movirulz_stremio import Movierulz
#from tamilblasters_stremio import Tamilblasters

app = Flask(__name__)

# Streaks_Movies Manifest
MANIFEST = {
    'id': 'org.stremio.Streaks_Movies',
    'version': '1.0.0',

    'name': 'Streaks Movies',
    'description': 'Add-on for Streaming Indian Regional Movies. As of version_2 only 2 Domains is supported',

    'types': ['movie'],

    'catalogs': [],

    'resources': [
        {'name': 'stream', 'types': [
            'movie'], 'idPrefixes': ['tt', 'hpy']}
    ]
}


# Intial for STREAMS dictionary Later would be populated by search results
STREAMS = {
    'movie': {}
}

# Helper function for JSON response
def respond_with(data):
    resp = jsonify(data)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Headers'] = '*'
    return resp

@app.route('/manifest.json')
def addon_manifest():
    return respond_with(MANIFEST)

@app.route('/stream/<type>/<id>.json')
def addon_stream(type, id):
    if type not in MANIFEST['types']:
        abort(404)

    title=imdb_retriver.fetch_movie_title(id)
    stream_1=Tamilmv.tamilmv(title,id)
    stream_2=Movierulz.movierulz(title,id)
    #stream_3=Tamilblasters.tamilblasters(title,id)

    if id not in STREAMS['movie']:
            STREAMS['movie'][id] = []
    STREAMS['movie'][id].extend(stream_1)
    STREAMS['movie'][id].extend(stream_2)
    #STREAMS['movie'][id].extend(stream_3)

    streams = {'streams': []}
    if type in STREAMS and id in STREAMS[type]:
        streams['streams'] = STREAMS[type][id]
    return respond_with(streams)

if __name__ == '__main__':
    app.run(debug=True)