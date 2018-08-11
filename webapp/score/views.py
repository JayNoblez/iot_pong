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
    template = loader.get_template('leaderboard.html')
    ordered_players = Player.objects.order_by('score').reverse()
    context = {'players' : ordered_players}
    return HttpResponse(template.render(context, request))

def scoreboard(request):
    template = loader.get_template('scoreboard.html')
    context = {'games' : Game.objects.order_by('created').reverse()}
    return HttpResponse(template.render(context, request))
