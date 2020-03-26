#import libraries to extract data out of Spotify's API
import spotipy
import spotipy.util as util

class SpotifyAccess:
    
    def __init__(self, user_id, scope, cid, secret, redirect_uri):
        self.user_id = user_id
        self.scope = scope
        self.cid = cid
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.playlist_ids = {}
        self.track_objects = []
        self.tracks = {}
        self.audio_features_list = []
    
    def get_spotify_auth(self):
        '''
        INPUT: user_id, scope, client_id, client_secret, redirect_uri
        PROCESSING: call to Spotify's API, access token and authenticate
        OUTPUT: return token 
        '''
        token = util.prompt_for_user_token(self.user_id,
                               self.scope,
                               client_id=self.cid,
                               client_secret=self.secret,
                               redirect_uri=self.redirect_uri)
        self.sp = spotipy.Spotify(auth=token)  
        return self.sp
        
    def get_user_playlist_id(self, user_id):
        '''
        INPUT: user_id
        PROCESSING: extracts playlist objects from Spotify and store playlist ids in a dictionary
        OUTPUT: return all user playlist ids
        '''
        playlists = self.sp.user_playlists(user_id)
        for pl in playlists['items']:
            self.playlist_ids[pl['name']] = pl['id']

        return self.playlist_ids
    
    def get_all_track_objects(self, playlist_id):
        '''
        INPUT: playlist id (singular)
        PROCESSING: iterate through each track objects in a playlist and append it to a list
        OUTPUT: return all track objects in a playlist
        '''
        objects = self.sp.playlist_tracks(playlist_id)
        while objects:
            self.track_objects += objects['items']
            if objects['next']:
                objects = self.sp.next(objects)
            else:
                break
        return self.track_objects
    
    def get_track_info(self, track_objects):
        '''
        INPUT: list of track objects
        PROCESSING: iterate through each track object and extract high level track metadata from Spotify
        OUTPUT: track name/id, artist name/id, track release date, album type and popularity from each track object
        '''
        for obj in track_objects:
            try:
                #get track id -- use as dict key
                track_id = obj['track']['id']
                #get track name
                track_name = obj['track']['name']
                
                #get artist name/id: account for multiple artists
                artist_name = []
                artist_id = []
                for c, artists in enumerate(obj['track']['artists']):
                    artist_name.append(artists['name'])
                    artist_id.append(artists['id'])
                
                #get release date
                release_date = obj['track']['album']['release_date']
                
                #get album type
                album_type = obj['track']['album']['album_type']
                
                #get popularity
                popularity = obj['track']['popularity']
            except:
                pass
            
            self.tracks[track_id] = [track_name, artist_name, artist_id, release_date, album_type, popularity]
        return self.tracks
    
    def get_audio_features(self, track_list):
        '''
        INPUT: list of tracks
        PROCESSING: iterate through each track and extract audio features
        OUTPUT: return all audio features from a list of track ids
        '''
        try:
            #split track list into lists of max 50 id's 
            track_list_50 = [track_list[x:x+50] for x in range(0, len(track_list), 50)]
            
            #grab audio features in chunks of 50 dictionaries
            audio_features = [self.sp.audio_features(tracks=track_ids) for track_ids in track_list_50]
            
            #turn audio_features into one single list
            self.audio_features_list = [feature_dict for feature_list in audio_features for feature_dict in feature_list]
        except:
            pass
        
        return self.audio_features_list

