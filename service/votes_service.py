import os, sys
from database import db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import Votes

def _add_song_no_votes(song_id):
    new_song = Votes(song_id=song_id, jammer=0, not_jammer=0)
    db.session.add(new_song)
    db.session.commit()

def _add_vote(song_id, is_jammer):
    song = Votes.query.filter(Votes.song_id == song_id).first()
    if not song:
        _add_song_no_votes(song_id)
        song = Votes.query.filter(Votes.song_id == song_id).first()
    if is_jammer:
        song.jammer = Votes.jammer + 1
    else:
        song.not_jammer = Votes.not_jammer + 1
    db.session.commit()
    jammer = song.jammer
    not_jammer = song.not_jammer
    return jammer, not_jammer
    

def add_thumbs_up_vote(song_id):
    jammer, not_jammer = _add_vote(song_id, True)
    return {"song_id": song_id, "jammer": jammer, "not_jammer": not_jammer}

def add_thumbs_down_vote(song_id):
    jammer, not_jammer = _add_vote(song_id, False)
    return {"song_id": song_id, "jammer": jammer, "not_jammer": not_jammer}