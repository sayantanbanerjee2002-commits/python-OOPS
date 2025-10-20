from datetime import datetime
from typing import List, Dict
import random 

class Content: # Represent base class for all content types
    
    def __init__(self, title: str, genre: str, duration: int, rating: str, release_year: int):
        self.title = title              # Name of the content
        self.genre = genre              # Action, Comedy, Drama, etc.
        self.duration = duration        # Total duration in minutes
        self.rating = rating            # PG, PG-13, R, TV-MA, etc.
        self.release_year = release_year
        
    def calculate_watch_time(self) -> int:
     # method for returning total watch time
        return self.duration
    
    def get_age_restriction(self) -> int: # Determinr the minimum age 
        age_restrictions = {
            'G': 0,       # General audiences
            'PG': 7,      # Parental guidance
            'PG-13': 13,  # Parents strongly cautioned
            'R': 17,      # Restricted
            'TV-MA': 18,  # Mature audiences only
            'TV-14': 14,
            'TV-PG': 7
        }
        return age_restrictions.get(self.rating, 18)  # Default to 18 if unknown
    
    def __str__(self): # method for string readable
        return f"{self.title} ({self.release_year}) - {self.genre}"


class Movie(Content): # Represent Movie class with specific content
    
    def __init__(self, title: str, genre: str, duration: int, rating: str, 
                 release_year: int, director: str, cast_list: List[str], 
                 language: str, subtitles: List[str]):
        # Call parent constructor to set common properties
        super().__init__(title, genre, duration, rating, release_year)
        self.director = director
        self.cast_list = cast_list      # List of actor names
        self.language = language        # Original language
        self.subtitles = subtitles      # Available subtitle languages
        
    def __str__(self): # Improve readability of the string
        return f" Movie: {super().__str__()} | Dir: {self.director}"


class TVSeries(Content): # Represent TV series class with specific attributes
  
    def __init__(self, title: str, genre: str, duration: int, rating: str, 
                 release_year: int, seasons: int, episodes_per_season: List[int], 
                 episode_duration: int):
        super().__init__(title, genre, duration, rating, release_year)
        self.seasons = seasons
        self.episodes_per_season = episodes_per_season  
        self.episode_duration = episode_duration  # episode duratation      
        
    def calculate_watch_time(self) -> int:
        # Method to calculate Total time for a Series
        total_episodes = sum(self.episodes_per_season)
        return total_episodes * self.episode_duration
    
    def __str__(self):
        return f" TV Series: {super().__str__()} | {self.seasons} seasons"


class Documentary(Content): # Represent documentary class with Specific attributes
 
    def __init__(self, title: str, genre: str, duration: int, rating: str, 
                 release_year: int, topic: str, narrator: str, educational_rating: float):
        super().__init__(title, genre, duration, rating, release_year)
        self.topic = topic   # represent topic of the Documentary                   
        self.narrator = narrator  # represent name of the narrator           
        self.educational_rating = educational_rating  # 1-10 scale
        
    def __str__(self):
        return f" Documentary: {super().__str__()} | Topic: {self.topic}"


class Standup(Content):
   # Represent Stand_up comedy class with extra attributes
    def __init__(self, title: str, genre: str, duration: int, rating: str, 
                 release_year: int, comedian: str, venue: str, content_warning: str):
        super().__init__(title, genre, duration, rating, release_year)
        self.comedian = comedian
        self.venue = venue   # venue of Recording                  
        self.content_warning = content_warning  # Description about the content
        
    def __str__(self):
        return f" Standup: {super().__str__()} | Comedian: {self.comedian}"



class SubscriptionPlan: # Represent the class of different types of members
  
    def __init__(self, plan_name: str, price: float, simultaneous_streams: int, 
                 video_quality: str):
        self.plan_name = plan_name              # "Basic", "Standard", "Premium"
        self.price = price                      # Monthly price
        self.simultaneous_streams = simultaneous_streams  # How many devices at once
        self.video_quality = video_quality      # "SD", "HD", "4K"
        
    def __str__(self):
        return f"{self.plan_name} Plan: ${self.price}/mo | {self.video_quality} | {self.simultaneous_streams} streams"



class ViewingSession: # Trackes a single viewing Session
  
    def __init__(self, user: 'User', content: Content):
        self.user = user
        self.content = content
        self.start_time = datetime.now()
        self.progress = 0               # Percentage watched (0-100)
        self.watch_duration = 0         # Minutes watched in this session
        self.completed = False
        
    def update_progress(self, minutes_watched: int):
     # Method to get the the update about viewing Session
        self.watch_duration += minutes_watched
        total_duration = self.content.calculate_watch_time()
        self.progress = min((self.watch_duration / total_duration) * 100, 100)
        
        # Mark as completed if watched 90% or more
        if self.progress >= 90:
            self.completed = True
            
    def __str__(self):
        return f"{self.user.username} watching {self.content.title} - {self.progress:.1f}% complete"




class User: # Represent User Class with history
   
    def __init__(self, username: str, age: int, subscription_plan: SubscriptionPlan):
        self.username = username
        self.age = age
        self.subscription_plan = subscription_plan
        self.watch_history: List[Content] = []      # What they've watched
        self.watchlist: List[Content] = []          # What they want to watch
        self.preferences: Dict[str, any] = {        # Their preferences
  
        }
        self.viewing_sessions: List[ViewingSession] = []
        
    def add_to_watchlist(self, content: Content):
        """
        Add content to 'My List' / 'Watch Later'.
        """
        if content not in self.watchlist:
            self.watchlist.append(content)
            print(f" '{content.title}' added to {self.username}'s watchlist")
        else:
            print(f"'{content.title}' is already in your watchlist")
            
    def remove_from_watchlist(self, content: Content):
        """
        Remove content from watchlist.
        """
        if content in self.watchlist:
            self.watchlist.remove(content)
            print(f" '{content.title}' removed from watchlist")
            
    def check_age_restriction(self, content: Content) -> bool:
        """
        Verify if user is old enough to watch content.
        """
        required_age = content.get_age_restriction()
        if self.age >= required_age:
            return True
        else:
            print(f" Age restriction: '{content.title}' requires age {required_age}+. You are {self.age}.")
            return False
            
    def start_watching(self, content: Content) -> ViewingSession:
        """
        Start a new viewing session.
        """
        # Check age restriction first
        if not self.check_age_restriction(content):
            return None
            
        # Create new viewing session
        session = ViewingSession(self, content)
        self.viewing_sessions.append(session)
        
        # Add to watch history if not already there
        if content not in self.watch_history:
            self.watch_history.append(content)
            
        # Update preferences with genre
        if content.genre not in self.preferences['favorite_genres']:
            self.preferences['favorite_genres'].append(content.genre)
            
        print(f"  {self.username} started watching: {content.title}")
        return session
        
    def continue_watching(self) -> List[ViewingSession]:
        """
        Get list of unfinished content (continue watching feature).
        """
        # Find sessions that are started but not completed
        in_progress = [s for s in self.viewing_sessions 
                      if not s.completed and s.progress > 0]
        
        # Sort by most recently watched
        in_progress.sort(key=lambda s: s.start_time, reverse=True)
        
        return in_progress
        
    def get_recommendations(self, all_content: List[Content], count: int = 5) -> List[Content]:
        """
        Recommend content based on watch history and preferences.
        Algorithm:
        1. Find favorite genres from watch history
        2. Look for unwatched content in those genres
        3. Prioritize recent releases
        4. Filter by age restrictions
        """
        if not self.watch_history:
            # New user - recommend popular recent content
            eligible = [c for c in all_content if self.check_age_restriction(c)]
            return sorted(eligible, key=lambda c: c.release_year, reverse=True)[:count]
        
        # Count genre frequency in watch history
        genre_counts = {}
        for content in self.watch_history:
            genre_counts[content.genre] = genre_counts.get(content.genre, 0) + 1
            
        # Get favorite genres (top 3)
        favorite_genres = sorted(genre_counts.keys(), 
                                key=lambda g: genre_counts[g], 
                                reverse=True)[:3]
        
        # Find unwatched content in favorite genres
        recommendations = []
        for content in all_content:
            # Skip if already watched
            if content in self.watch_history:
                continue
                
            # Check age restriction
            if not self.check_age_restriction(content):
                continue
                
            # Prioritize favorite genres
            if content.genre in favorite_genres:
                recommendations.append(content)
                
        # Sort by release year (newer first)
        recommendations.sort(key=lambda c: c.release_year, reverse=True)
        
        return recommendations[:count]
        
    def search_content(self, all_content: List[Content], 
                      title: str = None, genre: str = None, 
                      release_year: int = None) -> List[Content]:
        """
        Search content with filters.
        """
        results = all_content.copy()
        
        # Filter by title (partial match, case-insensitive)
        if title:
            results = [c for c in results if title.lower() in c.title.lower()]
            
        # Filter by genre
        if genre:
            results = [c for c in results if c.genre.lower() == genre.lower()]
            
        # Filter by release year
        if release_year:
            results = [c for c in results if c.release_year == release_year]
            
        # Filter by age restriction
        results = [c for c in results if self.check_age_restriction(c)]
        
        return results
        
    def __str__(self):
        return f"User: {self.username} | {self.subscription_plan.plan_name} | Age: {self.age}"



def main():
    """
    Demonstration of the streaming service system.
    """
    print("=" * 60)
    print(" NETFLIX-LIKE STREAMING SERVICE DEMO")
    print("=" * 60)
    
    # Create subscription plans
    print("\n📋 Creating Subscription Plans...")
    basic_plan = SubscriptionPlan("Basic", 8.99, 1, "SD")
    standard_plan = SubscriptionPlan("Standard", 13.99, 2, "HD")
    premium_plan = SubscriptionPlan("Premium", 17.99, 4, "4K")
    print(basic_plan)
    print(standard_plan)
    print(premium_plan)
    
    # Create content library
    print("\n\n Creating Content Library...")
    content_library = [
        Movie("The Matrix", "Sci-Fi", 136, "R", 1999, "Wachowski Sisters", 
              ["Keanu Reeves", "Laurence Fishburne"], "English", ["Spanish", "French"]),
        
        Movie("Inception", "Sci-Fi", 148, "PG-13", 2010, "Christopher Nolan", 
              ["Leonardo DiCaprio", "Tom Hardy"], "English", ["Spanish", "French", "German"]),
        
        TVSeries("Stranger Things", "Horror", 0, "TV-14", 2016, 4, [8, 9, 8, 9], 50),
        
        TVSeries("Breaking Bad", "Drama", 0, "TV-MA", 2008, 5, [7, 13, 13, 13, 16], 47),
        
        Documentary("Planet Earth", "Nature", 550, "PG", 2006, "Wildlife", 
                   "David Attenborough", 9.5),
        
        Standup("Dave Chappelle: Sticks & Stones", "Comedy", 65, "TV-MA", 2019, 
               "Dave Chappelle", "Atlanta", "Strong language, adult themes"),
        
        Movie("Toy Story", "Animation", 81, "G", 1995, "John Lasseter", 
              ["Tom Hanks", "Tim Allen"], "English", ["Spanish"])
    ]
    
    for content in content_library:
        print(content)
    
    # Create users
    print("\n\n Creating Users...")
    adult_user = User("JohnDoe", 25, premium_plan)
    teen_user = User("TeenUser", 15, standard_plan)
    child_user = User("KidUser", 8, basic_plan)
    
    print(adult_user)
    print(teen_user)
    print(child_user)
    
    # Demo: Adult user watching content
    print("\n\n" + "=" * 60)
    print("DEMO 1: Adult User Watching Content")
    print("=" * 60)
    
    # Start watching a movie
    session1 = adult_user.start_watching(content_library[0])  # The Matrix
    session1.update_progress(60)  # Watched 60 minutes
    print(f"Progress: {session1.progress:.1f}%")
    
    # Watch another
    session2 = adult_user.start_watching(content_library[3])  # Breaking Bad
    session2.update_progress(200)  # Watched multiple episodes
    print(f"Progress: {session2.progress:.1f}%")
    
    # Demo: Continue watching
    print("\n\n" + "=" * 60)
    print("DEMO 2: Continue Watching Feature")
    print("=" * 60)
    
    continue_list = adult_user.continue_watching()
    print(f"\n{adult_user.username}'s Continue Watching:")
    for session in continue_list:
        print(f"  - {session.content.title}: {session.progress:.1f}% complete")
    
    # Demo: Watchlist
    print("\n\n" + "=" * 60)
    print("DEMO 3: Watchlist Feature")
    print("=" * 60)
    
    adult_user.add_to_watchlist(content_library[1])  # Inception
    adult_user.add_to_watchlist(content_library[4])  # Planet Earth
    adult_user.add_to_watchlist(content_library[1])  # Try adding Inception again
    
    print(f"\n{adult_user.username}'s Watchlist:")
    for content in adult_user.watchlist:
        print(f"  - {content.title}")
    
    # Demo: Age restrictions
    print("\n\n" + "=" * 60)
    print("DEMO 4: Age Restriction Checking")
    print("=" * 60)
    
    print(f"\nChild user ({child_user.username}, age {child_user.age}) trying to watch:")
    child_user.start_watching(content_library[3])  # Breaking Bad (TV-MA) - Should be blocked
    child_user.start_watching(content_library[6])  # Toy Story (G) - Should work
    
    # Demo: Recommendations
    print("\n\n" + "=" * 60)
    print("DEMO 5: Recommendation System")
    print("=" * 60)
    
    recommendations = adult_user.get_recommendations(content_library, count=3)
    print(f"\nRecommendations for {adult_user.username}:")
    for content in recommendations:
        print(f"  - {content}")
    
    # Demo: Search functionality
    print("\n\n" + "=" * 60)
    print("DEMO 6: Search with Filters")
    print("=" * 60)
    
    # Search by genre
    print("\nSearching for Sci-Fi content:")
    results = adult_user.search_content(content_library, genre="Sci-Fi")
    for content in results:
        print(f"  - {content}")
    
    # Search by title
    print("\nSearching for 'Earth':")
    results = adult_user.search_content(content_library, title="Earth")
    for content in results:
        print(f"  - {content}")
    
    # Demo: Polymorphism - calculate_watch_time()
    print("\n\n" + "=" * 60)
    print("DEMO 7: Polymorphism - Calculate Watch Time")
    print("=" * 60)
    
    print("\nTotal watch time for different content types:")
    for content in content_library[:5]:
        print(f"  - {content.title}: {content.calculate_watch_time()} minutes")
    
    print("\n" + "=" * 60)
    print(" DEMO COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()