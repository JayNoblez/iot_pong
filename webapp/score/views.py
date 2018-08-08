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
    print(str(ordered_players))
    context = {'players' : ordered_players}
    return HttpResponse(template.render(context, request))

def scoreboard(request):
    template = loader.get_template('scoreboard.html')
    context = {'games' : Game.objects.all().reverse()}
    return HttpResponse(template.render(context, request))

def log_game(request):
    """Set the preference of a movie"""
    #if request.user.is_authenticated and request.is_ajax() and request.POST.get('video') != None:
    if request.is_ajax() and request.POST.get('uid') != None:
        obj = Game(uid=request.POST.get('uid'), score_player_1=request.POST.get('score_player_1'), score_player_2=request.POST.get('score_player_2'), name_player_1=request.POST.get('name_player_1'), name_player_2=request.POST.get('name_player_2'))
        obj.save()

        obj = Player.objects.filter(name=request.POST.get('name_player_1'))
        if obj:
            new_score = int(request.POST.get('score_player_1')) - int(request.POST.get('score_player_2')) + obj.score
            obj.update(score=new_score)
            obj.save()
        else:
            obj = Player(name=request.POST.get('name_player_1'), score=(int(request.POST.get('score_player_1')) - int(request.POST.get('score_player_2'))))
            obj.save()

        obj = Player.objects.filter(name=request.POST.get('name_player_2'))
        if obj:
            new_score = int(request.POST.get('score_player_2')) - int(request.POST.get('score_player_1')) + obj.score
            obj.update(score=new_score)
            obj.save()
        else:
            obj = Player(name=request.POST.get('name_player_2'), score=(int(request.POST.get('score_player_2')) - int(request.POST.get('score_player_1'))))
            obj.save()

        print("OK")

        return HttpResponse(request.POST.get('name_player_1') + ',' + request.POST.get('score_player_1') + ',' + request.POST.get('name_player_2') + ',' + request.POST.get('score_player_2'))
    else:
        return HttpResponse('')