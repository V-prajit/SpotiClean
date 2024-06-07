import os
import spotipy
from flask import Flask, session, url_for, redirect, request
import config
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
scope = 'playlist-modify-public, playlist-modify-private, playlist-read-private'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=config.SPOTIPY_CLIENT_ID,
    client_secret=config.SPOTIPY_CLIENT_SECRET,
    redirect_uri=config.SPOTIPY_REDIRECT_URI,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)

@app.route('/')
def home():
    print("hit home page")
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        print(f'Redirecting to: {auth_url}')
        return redirect(auth_url)
    return redirect(url_for('get_playlist'))

@app.route('/callback')
def callback():
    print('entered call block')
    session.clear()
    code = request.args.get('code')
    print(f'Auth code received{code}')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    print(f'Token info: {token_info}')
    return redirect(url_for('get_playlist'))

@app.route('/playlists')
def get_playlist():
    print('Accessed playlist route')
    token_info = session.get('token_info', None)
    if not token_info:
        print('no token info found redirecting to home')
        return redirect('/')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']
    playlists = sp.current_user_playlists(limit=50, offset=0)
    print(f'User ID: {user_id}')
    print(f'Playlists: {playlists}')

    if playlists['items']:
        return "<br>".join([f"{idx + 1}. {playlist['name']}" for idx, playlist in
                            enumerate(playlists['items'])])
    else:
        return "No Playlist Found"

if __name__ == '__main__':
    app.run(debug=True, port=5000)