import os
import json
import sys

from flask import session
from flask_restx import Api, Namespace, Resource
from flask.wrappers import Response
from marshmallow import ValidationError

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from service.song_service import get_random_song
from service.votes_service import add_thumbs_down_vote, add_thumbs_up_vote


########################################################################################################################
# Config
########################################################################################################################

VERSION = "v1"
api = Api(
    title="jammer-song-selector",
    version=VERSION,
    prefix=f"/api/{VERSION}",
    doc="/docs" if os.getenv("FLASK_ENV") == "development" else False,
)


@api.errorhandler(ValidationError)
def handle_validation_error(error: ValidationError):
    del error.data
    return {"message": error.messages}, 400


########################################################################################################################
# Namespaces
########################################################################################################################

song = Namespace('song', description='Endpoints for songs')
api.add_namespace(song, path="/song")

@song.route('/random')
class RandomSong(Resource):
    """Random song"""
    def get(self):
        """Get a random song from the Spotify API"""
        random_song_obj = get_random_song()
        song_id = random_song_obj["id"]
        while song_id in session:
            random_song_obj = get_random_song()
            song_id = random_song_obj["id"]
        return Response(json.dumps(random_song_obj), mimetype='application/json')


vote = Namespace('votes', description='Endpoints for votes')
api.add_namespace(vote, path="/vote")

@vote.route('/jammer/<song_id>')
@vote.param('song_id', 'Spotify Song ID')
class Jammer(Resource):
    """Vote if certified jammer"""
    def post(self, song_id):
        """Upvote a song if user has not voted yet"""
        if song_id not in session:
            status = add_thumbs_up_vote(song_id)
            session[song_id] = 1
            return Response(json.dumps(status), mimetype='application/json')
        return Response(json.dumps({"status": "User already voted in session"}), mimetype='application/json')
    

@vote.route('/not_jammer/<song_id>')
@vote.param('song_id', 'Spotify Song ID')
class NotJammer(Resource):
    """Vote if NOT jammer"""
    def post(self, song_id):
        """Downvote a song if user has not voted yet"""
        if song_id not in session:
            status = add_thumbs_down_vote(song_id)
            session[song_id] = 1
            return Response(json.dumps(status), mimetype='application/json')
        return Response(json.dumps({"status": "User already voted in session"}), mimetype='application/json')

@vote.route('/clear_session')
class ClearSession(Resource):
    """Reset client side vote list by flushing the session cookie"""
    def post(self):
        """Flush session cookie"""
        session.clear()
        return Response(json.dumps({"status": "Session cookie cleared"}), mimetype='application/json')
