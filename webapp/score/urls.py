from django.urls import path

from . import views
from .models import Game
from .models import Player

urlpatterns = [
    path('', views.index, name='index'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
]


import paho.mqtt.client as mqtt

def decode(string):
	return tuple(string.split(','))

def on_connect(client, userdata, flags, rc):
    client.subscribe("thm_rr_iot_project/session/#")

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    if msg.topic == "thm_rr_iot_project/session/game":
        uid, name_player_1, score_player_1, name_player_2, score_player_2 = decode(msg.payload.decode("utf-8"))
        g = Game(uid=uid, score_player_1=int(score_player_1), score_player_2=int(score_player_2), name_player_1=name_player_1, name_player_2=name_player_2)
        g.save()

        print(name_player_1)
        print(str(score_player_1))
        print(name_player_2)
        print(str(score_player_2))

        obj = Player.objects.filter(name=name_player_1)
        if obj:
            new_score = int(score_player_1) - int(score_player_2) + obj[0].score
            print(score_player_1 + " new score: " + str(new_score))
            obj.update(score=new_score)
        else:
            p = Player(name=name_player_1, score=(int(score_player_1) - int(score_player_2)))
            p.save()

        obj = Player.objects.filter(name=name_player_2)
        if obj:
            new_score = int(score_player_2) - int(score_player_1) + obj[0].score
            print(score_player_2 + " new score: " + str(new_score))
            obj.update(score=new_score)
        else:
            p = Player(name=name_player_2, score=(int(score_player_2) - int(score_player_1)))
            p.save()

from score.models import Game
client = mqtt.Client()

# Set mqtt callbacks
client.on_connect = on_connect
client.on_message = on_message
client.connect("iot.eclipse.org", 1883, 60)
client.loop_start()