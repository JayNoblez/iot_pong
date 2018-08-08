from django.db import models

class Game(models.Model):
    uid = models.CharField(max_length=200)
    name_player_1 = models.CharField(max_length=10)
    name_player_2 = models.CharField(max_length=10)
    score_player_1 = models.IntegerField(default=0)
    score_player_2 = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

class Player(models.Model):
	name = models.CharField(max_length=10)
	score = models.IntegerField(default=0)
