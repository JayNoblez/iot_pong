from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import Game
from .models import Player

def index(request):
    template = loader.get_template('score.html')
    context = {}
    return HttpResponse(template.render(context, request))

def leaderboard(request):
    """View for the leaderboard. Returns a HttpResponse with all
       players and their scores"""
    template = loader.get_template('leaderboard.html')
    # Get all players
    ordered_players = Player.objects.order_by('score').reverse() # Reverse since first player is last in the list
    context = {'players' : ordered_players}
    return HttpResponse(template.render(context, request))

def scoreboard(request):
    """View for the scoreboard. Returns a HttpResponse with all
       players and their scores"""
    template = loader.get_template('scoreboard.html')
    # Get all games
    context = {'games' : Game.objects.order_by('created').reverse()}
    return HttpResponse(template.render(context, request))

from .models import Game
from .models import Player
import paho.mqtt.client as mqtt

# The following the continously running thread that looks for finished games and logs them
def decode(string):
    """Used to decode a comma delimited string"""
    return tuple(string.split(','))

def on_connect(client, userdata, flags, rc):
    """Callback called on connection with broker"""
    client.subscribe("thm_rr_iot_project/session/#") # Subscribe to session/game as this is where finished games are published

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    if msg.topic == "thm_rr_iot_project/session/game":
        print(msg.topic)
        # New finished game, log it and the players as well
        uid, name_player_1, score_player_1, name_player_2, score_player_2 = decode(msg.payload.decode("utf-8"))

        obj = Game.objects.filter(uid=uid)
        if obj:
            return # Do not touch existing games
        else:
            g = Game(uid=uid, score_player_1=int(score_player_1), score_player_2=int(score_player_2), name_player_1=name_player_1, name_player_2=name_player_2)
            g.save()

        obj = Player.objects.filter(name=name_player_1)
        if obj:
            # Update existing player
            new_score = int(score_player_1) - int(score_player_2) + obj[0].score
            obj.update(score=new_score)
        else:
            # Create new player and save
            p = Player(name=name_player_1, score=(int(score_player_1) - int(score_player_2)))
            p.save()

        obj = Player.objects.filter(name=name_player_2)
        if obj:
            new_score = int(score_player_2) - int(score_player_1) + obj[0].score
            obj.update(score=new_score)
        else:
            p = Player(name=name_player_2, score=(int(score_player_2) - int(score_player_1)))
            p.save()

client = mqtt.Client()

# Set mqtt callbacks
client.on_connect = on_connect
client.on_message = on_message
client.connect("iot.eclipse.org", 1883, 60)
client.loop_start()
