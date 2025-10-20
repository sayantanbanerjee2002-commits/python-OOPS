from datetime import datetime, timedelta
from collections import Counter
import random


class Song:
    """Represents a single song/track"""
    
    def __init__(self, song_id, title, artist, album, duration):
        self.song_id = song_id
        self.title = title
        self.artist = artist  # Reference to Artist object
        self.album = album  # Reference to Album object
        self.duration = duration  # Duration in seconds
        self.play_count = 0
        self.likes = 0
    
    def play(self):
        """Increment play count when song is played"""
        self.play_count += 1
    
    def like(self):
        """Increment like count"""
        self.likes += 1
    
    def __str__(self):
        return f"{self.title} by {self.artist.name} ({self.duration}s)"
    
    def __repr__(self):
        return f"Song({self.title})"


class Album:
    """Represents an album containing multiple songs"""
    
    def __init__(self, album_id, title, artist, release_date):
        self.album_id = album_id
        self.title = title
        self.artist = artist  # Reference to Artist object
        self.release_date = release_date
        self.songs_list = []  # Composition: Album contains Songs
        self.total_duration = 0
    
    def add_song(self, song):
        """Add a song to the album"""
        self.songs_list.append(song)
        self.total_duration += song.duration
    
    def __str__(self):
        return f"Album: {self.title} by {self.artist.name} ({len(self.songs_list)} songs)"


class Artist:
    """Represents a music artist/band"""
    
    def __init__(self, artist_id, name, genre):
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.albums_list = []
        self.followers = 0
        self.monthly_listeners = 0
    
    def add_album(self, album):
        """Add an album to artist's discography"""
        self.albums_list.append(album)
    
    def calculate_royalty(self):
        """Calculate total royalty payments based on all song plays"""
        total_plays = 0
        for album in self.albums_list:
            for song in album.songs_list:
                total_plays += song.play_count
        
        royalty_per_play = 0.004
        total_royalty = total_plays * royalty_per_play
        return total_royalty
    
    def __str__(self):
        return f"Artist: {self.name} ({self.genre})"


class Playlist:
    """Represents a playlist that can be shared and collaborated on"""
    
    def __init__(self, playlist_id, name, creator):
        self.playlist_id = playlist_id
        self.name = name
        self.creator = creator  # User who created the playlist
        self.songs = []  # Composition: Playlist contains Songs
        self.is_public = False
        self.followers = 0
        self.collaborators = [creator]  # Users who can modify playlist
        self.shuffle_mode = False
        self.repeat_mode = False  # False, 'one', 'all'
        self._current_index = 0
        self._shuffled_indices = []
    
    def add_song(self, song, user):
        """Add song to playlist if user is a collaborator"""
        if user in self.collaborators:
            self.songs.append(song)
            return True
        return False
    
    def remove_song(self, song, user):
        """Remove song from playlist if user is a collaborator"""
        if user in self.collaborators and song in self.songs:
            self.songs.remove(song)
            return True
        return False
    
    def add_collaborator(self, user):
        """Allow another user to collaborate on playlist"""
        if user not in self.collaborators:
            self.collaborators.append(user)
    
    def toggle_shuffle(self):
        """Enable/disable shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        if self.shuffle_mode:
            # Create shuffled index list
            self._shuffled_indices = list(range(len(self.songs)))
            random.shuffle(self._shuffled_indices)
        else:
            self._shuffled_indices = []
    
    def set_repeat_mode(self, mode):
        """Set repeat mode: False, 'one', or 'all'"""
        self.repeat_mode = mode
    
    def __iter__(self):
        """Make playlist iterable to loop through songs"""
        self._current_index = 0
        return self
    
    def __next__(self):
        """Get next song based on shuffle/repeat settings"""
        if len(self.songs) == 0:
            raise StopIteration
        
        if self._current_index >= len(self.songs):
            if self.repeat_mode == 'all':
                self._current_index = 0
            else:
                raise StopIteration
        
        if self.shuffle_mode and self._shuffled_indices:
            song = self.songs[self._shuffled_indices[self._current_index]]
        else:
            song = self.songs[self._current_index]
        
        if self.repeat_mode == 'one':
            # Don't increment index for repeat one
            pass
        else:
            self._current_index += 1
        
        return song
    
    def get_total_duration(self):
        """Calculate total duration of all songs in playlist"""
        return sum(song.duration for song in self.songs)
    
    def __str__(self):
        return f"Playlist: {self.name} by {self.creator.name} ({len(self.songs)} songs)"


class User:
    """Represents a user of the music platform"""
    
    SUBSCRIPTION_LIMITS = {
        'Free': 0,
        'Premium': 50,
        'Family': 100
    }
    
    def __init__(self, user_id, name, subscription_tier='Free'):
        self.user_id = user_id
        self.name = name
        self.subscription_tier = subscription_tier
        self.playlists = []
        self.listening_history = []  # List of (song, timestamp) tuples
        self.liked_songs = []
        self.downloaded_songs = []
    
    def create_playlist(self, playlist_id, name):
        """Create a new playlist"""
        playlist = Playlist(playlist_id, name, self)
        self.playlists.append(playlist)
        return playlist
    
    def play_song(self, song):
        """Play a song and record it in history"""
        song.play()
        timestamp = datetime.now()
        self.listening_history.append((song, timestamp))
    
    def like_song(self, song):
        """Like a song"""
        if song not in self.liked_songs:
            self.liked_songs.append(song)
            song.like()
    
    def download_song(self, song):
        """Download song for offline listening (based on subscription)"""
        max_downloads = self.SUBSCRIPTION_LIMITS[self.subscription_tier]
        
        if len(self.downloaded_songs) < max_downloads:
            if song not in self.downloaded_songs:
                self.downloaded_songs.append(song)
                return True
        return False
    
    def get_recommendations(self, count=5):
        """Recommend songs based on listening history"""
        if not self.listening_history:
            return []
        
        # Count genre frequencies from listening history
        genre_counter = Counter()
        artist_counter = Counter()
        
        for song, _ in self.listening_history:
            genre_counter[song.artist.genre] += 1
            artist_counter[song.artist] += 1
        
        # Get top genres and artists
        top_genres = [genre for genre, _ in genre_counter.most_common(3)]
        top_artists = [artist for artist, _ in artist_counter.most_common(3)]
        
        # Find songs from top genres/artists not in history
        listened_songs = {song for song, _ in self.listening_history}
        recommendations = []
        
        for artist in top_artists:
            for album in artist.albums_list:
                for song in album.songs_list:
                    if song not in listened_songs and song not in recommendations:
                        recommendations.append(song)
                        if len(recommendations) >= count:
                            return recommendations
        
        return recommendations[:count]
    
    def get_yearly_wrap(self, year=None):
        """Generate yearly listening statistics"""
        if year is None:
            year = datetime.now().year
        
        # Filter history for the specified year
        year_history = [
            (song, ts) for song, ts in self.listening_history
            if ts.year == year
        ]
        
        if not year_history:
            return {
                'total_listening_time': 0,
                'top_artists': [],
                'top_genres': [],
                'top_songs': [],
                'total_songs_played': 0
            }
        
        # Calculate statistics
        total_time = sum(song.duration for song, _ in year_history)
        
        artist_counter = Counter(song.artist for song, _ in year_history)
        genre_counter = Counter(song.artist.genre for song, _ in year_history)
        song_counter = Counter(song for song, _ in year_history)
        
        return {
            'total_listening_time': total_time,
            'total_listening_time_formatted': f"{total_time // 3600}h {(total_time % 3600) // 60}m",
            'top_artists': [artist.name for artist, _ in artist_counter.most_common(5)],
            'top_genres': [genre for genre, _ in genre_counter.most_common(3)],
            'top_songs': [song.title for song, _ in song_counter.most_common(10)],
            'total_songs_played': len(year_history)
        }
    
    def __str__(self):
        return f"User: {self.name} ({self.subscription_tier})"


# ==DEMONSTRATION ==

def demo():
    """Demonstrate the music platform functionality"""
    
    print("=" * 60)
    print("SPOTIFY-LIKE MUSIC PLATFORM DEMO")
    print("=" * 60)
    
    # Create artists
    print("\n1. Creating Artists...")
    artist1 = Artist("A001", "The Weeknd", "R&B")
    artist2 = Artist("A002", "Taylor Swift", "Pop")
    print(f"   ✓ {artist1}")
    print(f"   ✓ {artist2}")
    
    # Create albums
    print("\n2. Creating Albums...")
    album1 = Album("AL001", "After Hours", artist1, "2020-03-20")
    album2 = Album("AL002", "Midnights", artist2, "2022-10-21")
    artist1.add_album(album1)
    artist2.add_album(album2)
    print(f"   ✓ {album1}")
    print(f"   ✓ {album2}")
    
    # Create songs
    print("\n3. Creating Songs...")
    song1 = Song("S001", "Blinding Lights", artist1, album1, 200)
    song2 = Song("S002", "Save Your Tears", artist1, album1, 215)
    song3 = Song("S003", "Anti-Hero", artist2, album2, 201)
    song4 = Song("S004", "Lavender Haze", artist2, album2, 202)
    
    album1.add_song(song1)
    album1.add_song(song2)
    album2.add_song(song3)
    album2.add_song(song4)
    
    print(f"   ✓ {song1}")
    print(f"   ✓ {song2}")
    print(f"   ✓ {song3}")
    print(f"   ✓ {song4}")
    
    # Create users
    print("\n4. Creating Users...")
    user1 = User("U001", "John Doe", "Premium")
    user2 = User("U002", "Jane Smith", "Family")
    print(f"   ✓ {user1}")
    print(f"   ✓ {user2}")
    
    # Users play songs
    print("\n5. Users Playing Songs...")
    for _ in range(1000):
        user1.play_song(song1)
    for _ in range(500):
        user1.play_song(song2)
    for _ in range(300):
        user1.play_song(song3)
    
    print(f"   ✓ {user1.name} played {song1.title} {song1.play_count} times")
    print(f"   ✓ {user1.name} played {song2.title} {song2.play_count} times")
    print(f"   ✓ {user1.name} played {song3.title} {song3.play_count} times")
    
    # Calculate artist royalties
    print("\n6. Calculating Artist Royalties...")
    royalty1 = artist1.calculate_royalty()
    royalty2 = artist2.calculate_royalty()
    print(f"   ✓ {artist1.name} earned: ${royalty1:.2f}")
    print(f"   ✓ {artist2.name} earned: ${royalty2:.2f}")
    
    # Create playlist
    print("\n7. Creating Playlist...")
    playlist = user1.create_playlist("P001", "My Favorites")
    playlist.add_song(song1, user1)
    playlist.add_song(song2, user1)
    playlist.add_song(song3, user1)
    print(f"   ✓ {playlist}")
    print(f"   ✓ Total duration: {playlist.get_total_duration()}s")
    
    # Collaborative playlist
    print("\n8. Adding Collaborator to Playlist...")
    playlist.add_collaborator(user2)
    playlist.add_song(song4, user2)
    print(f"   ✓ {user2.name} added {song4.title}")
    print(f"   ✓ Collaborators: {[u.name for u in playlist.collaborators]}")
    
    # Shuffle and iterate
    print("\n9. Playing Playlist with Shuffle...")
    playlist.toggle_shuffle()
    print(f"   ✓ Shuffle mode: {playlist.shuffle_mode}")
    print("   ✓ Playing first 3 songs:")
    count = 0
    for song in playlist:
        print(f"      → {song}")
        count += 1
        if count >= 3:
            break
    
    # Download songs
    print("\n10. Downloading Songs (Offline Mode)...")
    max_downloads = User.SUBSCRIPTION_LIMITS[user1.subscription_tier]
    print(f"   ✓ {user1.name} can download {max_downloads} songs")
    user1.download_song(song1)
    user1.download_song(song2)
    print(f"   ✓ Downloaded: {len(user1.downloaded_songs)} songs")
    
    # Get recommendations
    print("\n11. Getting Song Recommendations...")
    recommendations = user1.get_recommendations(3)
    print(f"   ✓ Recommendations for {user1.name}:")
    for rec in recommendations:
        print(f"      → {rec}")
    
    # Yearly wrap-up
    print("\n12. Yearly Wrap-Up...")
    wrap = user1.get_yearly_wrap(2025)
    print(f"   ✓ Total listening time: {wrap['total_listening_time_formatted']}")
    print(f"   ✓ Top artists: {', '.join(wrap['top_artists'])}")
    print(f"   ✓ Top genres: {', '.join(wrap['top_genres'])}")
    print(f"   ✓ Total songs played: {wrap['total_songs_played']}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)


# Run the demonstration
if __name__ == "__main__":
    demo()