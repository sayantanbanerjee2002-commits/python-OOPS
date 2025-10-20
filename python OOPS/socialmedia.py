from datetime import datetime
from typing import List, Set, Optional


class Comment: # Represents a comment on a post with support for nested replies.
    
    def __init__(self, text: str, author: 'User', parent_comment: Optional['Comment'] = None):
    # Initialize the Comment with argument text,author,parent_comment
        self.text = text
        self.author = author
        self.timestamp = datetime.now()
        self.replies: List['Comment'] = []
        self.parent_comment = parent_comment
        
        # If this is a reply, add it to parent's replies list
        if parent_comment:
            parent_comment.replies.append(self)
    
    def reply(self, text: str, author: 'User') -> 'Comment':
       #    Add a reply to this comment.
        
        # Args:
        #     text: Reply content
        #     author: User writing the reply
            
        # Returns:
        #     The newly created reply comment
        return Comment(text, author, parent_comment=self)
    
    def __str__(self) -> str: # String representation of comment
        reply_count = len(self.replies)
        return f"@{self.author.username}: {self.text} ({reply_count} replies)"


class Post: # Represents a social media post with engagement features
    
    def __init__(self, content: str, author: 'User'):
       # Intialize a post with content and author
        self.content = content
        self.author = author
        self.timestamp = datetime.now()
        self.likes: Set['User'] = set()  # Using set to prevent duplicate likes
        self.comments: List[Comment] = []
        self._shares: List['User'] = []
    
    def like(self, user: Optional['User'] = None) -> 'Post':
      # method of like the post by method chaining
        if user:
            self.likes.add(user)
        return self
    
    def unlike(self, user: 'User') -> 'Post':
       # remove a like from the post by method chaining
        self.likes.discard(user)
        return self
    
    def comment(self, text: str = None, author: 'User' = None) -> 'Post':
        # Add a comment to the post by Method chaining
        if text and author:
            new_comment = Comment(text, author)
            self.comments.append(new_comment)
        return self
    
    def share(self, user: Optional['User'] = None) -> 'Post':
      # method for share the post
        if user:
            self._shares.append(user)
        return self
    
    def get_engagement_stats(self) -> dict:
      # Method for get engagement statistics
        return {
            'likes': len(self.likes),
            'comments': len(self.comments),
            'shares': len(self._shares)
        }
    
    def __str__(self) -> str:
        """String representation of post."""
        stats = self.get_engagement_stats()
        return f"@{self.author.username} ({self.timestamp.strftime('%Y-%m-%d %H:%M')}): {self.content}\n" \
               f" {stats['likes']} |  {stats['comments']} |  {stats['shares']}"


class Timeline:
    """Aggregates and displays posts from followed users."""
    
    def __init__(self, owner: 'User'): # Intialize timeline for a user
        self.owner = owner
    
    def get_posts(self, limit: int = 10) -> List[Post]:
     # Method to get Timelined post from followed users
        timeline_posts = []
        
        # Collect posts from all followed users
        for followed_user in self.owner.following:
            timeline_posts.extend(followed_user.posts)
        
        # Include own posts
        timeline_posts.extend(self.owner.posts)
        
        # Sort by timestamp (most recent first)
        timeline_posts.sort(key=lambda post: post.timestamp, reverse=True)
        
        return timeline_posts[:limit]
    
    def display(self, limit: int = 10) -> None: # Display the Timeline post
        posts = self.get_posts(limit)
        print(f"\n{'='*60}")
        print(f"Timeline for @{self.owner.username}")
        print(f"{'='*60}\n")
        
        if not posts:
            print("No posts to display. Follow some users!")
        else:
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post}")
                print("-" * 60)


class User:
    """Represents a social media user with profile and relationships."""
    
    def __init__(self, username: str, email: str): # Intialize the users
     
        self._username = username
        self._email = email
        self.followers: Set['User'] = set()
        self.following: Set['User'] = set()
        self.posts: List[Post] = []
        self.timeline = Timeline(self)  # Composition: User has-a Timeline
        self._profile_private = False
    
    # Property getters and setters for privacy control
    @property
    def username(self) -> str: # get username
        return self._username
    
    @property
    def email(self) -> str: # get Email(privacy protected)
        if self._profile_private:
            return "***@***.***"  # Hidden for private profiles
        return self._email
    
    @property
    def profile_private(self) -> bool:
        """Check if profile is private."""
        return self._profile_private
    
    @profile_private.setter
    def profile_private(self, value: bool) -> None: # Set profile privacy
        self._profile_private = value
        print(f"Profile privacy set to: {'Private' if value else 'Public'}")
    
    def follow(self, other_user: 'User') -> 'User':
      # Method to follow another users
        if other_user == self:
            print("You cannot follow yourself!")
            return self
        
        if other_user in self.following:
            print(f"You are already following @{other_user.username}")
            return self
        
        # Bidirectional update
        self.following.add(other_user)
        other_user.followers.add(self)
        
        print(f"@{self.username} is now following @{other_user.username}")
        return self
    
    def unfollow(self, other_user: 'User') -> 'User': # method to unfollow users
        if other_user not in self.following:
            print(f"You are not following @{other_user.username}")
            return self
        
        # Bidirectional update
        self.following.discard(other_user)
        other_user.followers.discard(self)
        
        print(f"@{self.username} unfollowed @{other_user.username}")
        return self
    
    def create_post(self, content: str) -> Post: # method to create new post with arguments content
        post = Post(content, self)
        self.posts.append(post)
        return post
    
    def get_follower_count(self) -> int:
        """Get number of followers."""
        return len(self.followers)
    
    def get_following_count(self) -> int:
        """Get number of users being followed."""
        return len(self.following)
    
    # Special methods for Pythonic interface
    def __len__(self) -> int: # method to return number of Followers
        return len(self.followers)
    
    def __contains__(self, other_user: 'User') -> bool: # check if the users follow other users or not
        return other_user in self.following
    
    def __str__(self) -> str:
        """String representation of user."""
        return f"@{self.username} | Followers: {len(self.followers)} | Following: {len(self.following)} | Posts: {len(self.posts)}"


# ============================================================================
# DEMONSTRATION: Complete Social Media System in Action
# ============================================================================

def main():
    """Demonstrate the social media backend system."""
    
    print("\n SOCIAL MEDIA BACKEND SYSTEM DEMO\n")
    
    # Create users
    print("  CREATING USERS")
    print("-" * 60)
    Sayantan = User("Sayantan", "Sayantan@example.com")
    Debasish = User("Debasish", "debasish@example.com")
    Suman = User("Suman", "Suman@example.com")
    Dev = User("Dev", "Dev@example.com")
    
    print(f"Created: {Sayantan}")
    print(f"Created: {Debasish}")
    print(f"Created: {Suman}")
    print(f"Created: {Dev}\n")
    
    # Test follow functionality with bidirectional updates
    print("  TESTING FOLLOW/UNFOLLOW (Bidirectional Updates)")
    print("-" * 60)
    Sayantan.follow(Debasish).follow(Suman)  # Method chaining
    Debasish.follow(Sayantan).follow(Dev)
    Sayantan.follow(Dev)
    Dev.follow(Sayantan).follow(Debasish).follow(Suman)
    print()
    
    # Test __len__ special method
    print(" TESTING __len__() FOR FOLLOWER COUNT")
    print("-" * 60)
    print(f"Sayantan has {len(Sayantan)} followers (using len())")
    print(f"Debasish has {len(Debasish)} followers (using len())")
    print(f"Suman has {len(Suman)} followers (using len())\n")
    
    # Test __contains__ special method
    print("  TESTING __contains__() TO CHECK IF USER FOLLOWS ANOTHER")
    print("-" * 60)
    print(f"Does Sayantan follow Debasish? {Debasish in Sayantan}")
    print(f"Does Debasish follow Suman? {Suman in Debasish}")
    print(f"Does Suman follow Dev? {Dev in Suman}\n")
    
    # Test unfollow
    print("  TESTING UNFOLLOW")
    print("-" * 60)
    Dev.unfollow(Suman)
    print(f"After unfollowing - Dev followers: {len(Dev)}\n")
    
    # Create posts
    print(" CREATING POSTS")
    print("-" * 60)
    post1 = Sayantan.create_post("Just discovered a magical rabbit hole! ")
    post2 = Debasish.create_post("Building something amazing today! ")
    post3 = Suman.create_post("Life is like a box of chocolates ")
    post4 = Dev.create_post("Coding all night!  #DevLife")
    print(f"Sayantan created: {post1.content}")
    print(f"Debasish created: {post2.content}")
    print(f"Suman created: {post3.content}")
    print(f"Dev created: {post4.content}\n")
    
    # Test method chaining for post actions
    print(" TESTING METHOD CHAINING: like().comment().share()")
    print("-" * 60)
    post1.like(Debasish).like(Sayantan).comment("Love this!", Debasish).comment("Amazing!", Suman).share(Dev)
    post2.like(Sayantan).like(Dev).comment("Great work!", Sayantan)
    post3.like(Sayantan).like(Debasish).like(Dev)
    print(" Method chaining executed successfully!\n")
    
    # Display post engagement
    print("  POST ENGAGEMENT STATISTICS")
    print("-" * 60)
    print(post1)
    print()
    print(post2)
    print()
    
    # Test nested comments (replies)
    print("9  TESTING NESTED COMMENTS (REPLIES)")
    print("-" * 60)
    comment1 = post1.comments[0]  # Debasish's comment
    reply1 = comment1.reply("Thanks! It was an adventure!", Sayantan)
    reply2 = comment1.reply("Tell us more!", Dev)
    print(f"Original comment: {comment1}")
    print(f"Reply 1: {reply1}")
    print(f"Reply 2: {reply2}\n")
    
    # Test Timeline (composition)
    print(" TESTING TIMELINE (User has-a Timeline)")
    print("-" * 60)
    Dev.timeline.display(limit=5)
    print()
    
    # Test privacy settings
    print(" TESTING PRIVACY SETTINGS (Property Getters/Setters)")
    print("-" * 60)
    print(f"Sayantan's email (public): {Sayantan.email}")
    Sayantan.profile_private = True
    print(f"Sayantan's email (private): {Sayantan.email}")
    Sayantan.profile_private = False
    print()
    
    # Summary statistics
    print(" FINAL STATISTICS")
    print("-" * 60)
    print(Sayantan)
    print(Debasish)
    print(Suman)
    print(Dev)
    print("\n Social Media Backend System Demo Complete!\n")


if __name__ == "__main__":
    main()