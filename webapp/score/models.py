from django.db import models

class Game(models.Model):
    """Model for an IoT pong game"""
    # Everything is provided by the players
    uid = models.CharField(max_length=200) # UID of the game
    name_player_1 = models.CharField(max_length=10) # Name of the first player (is 3 chars long but keep at 10 for future development)
    name_player_2 = models.CharField(max_length=10) # Name of the second player 
    score_player_1 = models.IntegerField(default=0) # Score of the first player
    score_player_2 = models.IntegerField(default=0) # Score of the second player
    created = models.DateTimeField(auto_now_add=True) # Timestamp of game (creation date is play date)

class Player(models.Model):
    """Model for an IoT pong player"""
    # Everything is provided by the players
    name = models.CharField(max_length=10) # Name of the player (is 3 chars long but keep at 10 for future development, change with above)
    score = models.IntegerField(default=0) # Score
