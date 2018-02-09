from django.shortcuts import render
import json
import logging

import telepot
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .utils import parse_new_game_names, parse_add_result
from carioca_game_telegram.models import Game, GameResult, Round, RoundResult

# Create your views here.

TelegramBot = telepot.Bot(settings.TELEGRAM_BOT_TOKEN)

logger = logging.getLogger('telegram.bot')

ROUNDS = (
        ('2T', '2 Trios'),
        ('1T1E', '1 Trio y 1 Escala'),
        ('2E', '2 Escalas'),
        ('3T', '3 Trios'),
        ('2T1E', '2 Trios y 1 Escala'),
        ('1T2E', '1 Trio y 2 Escalas'),
        ('4T', '4 Trios'),
        ('3E', '3 Estacalas'),  
    )

round_array = ['2T','1T1E','2E','3T','2T1E','1T2E','4T','3E']

def _display_help(chat_id):
    return render_to_string('help.md')

def _display_new_game(chat_id, names, lugar="Lugar no definido"):
    game = Game(lugar=lugar, jugadores=names, chat=chat_id)
    game.save()
    return render_to_string('newGame.md', {'items': parse_new_game_names(names), 'date': game.fecha, 'lugar': game.lugar})

def _display_start_game(chat_id):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')
    game = games[0]
    Game.objects.filter(id=game.id).update(start=True)
    round = Round(game=game, rounds="2T")
    round.save()
    return render_to_string('startGame.md', {'round': round})

def _display_add_player(chat_id, name):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')
    game=games[0]

    if game.start:
        return render_to_string('noNewPlayer.md')
    else:
        game.jugadores = game.jugadores+','+name
        game.save()
        return render_to_string('newPlayer.md',{'name':name})

def _display_delete_player(chat_id, name):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')
    game=games[0]
    
    if game.start:
        return render_to_string('noDeletePlayer.md')
    else:
        jugadores = game.jugadores.split(',')
        if name in jugadores:
            jugadores.remove(name)
            game.jugadores = ','.join(jugadores)
            game.save()
            return render_to_string('deletePlayer.md',{'name':name})
        else:
            return render_to_string('noPlayerToDelete.md',{'name':name})

def _display_players(chat_id):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')
    game=games[0]

    return render_to_string('players.md', {'items': parse_new_game_names(game.jugadores)})


def _display_actual_round(chat_id):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(game) == 0:
        return render_to_string('noGameError.md')

    game = games[0]
    if not game.start:
        return render_to_string('roundError.md')

    rounds = Round.objects.filter(game=game).filter(active=True)
    if len(rounds) == 0:
        return render_to_string('finalRoundError.md')

    round=rounds[0]
    return render_to_string('round.md', {'round': round})

def _display_next_round(chat_id):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')

    game = games[0]
    if not game.start:
        return render_to_string('roundError.md')
    
    names = game.jugadores.split(',')

    rounds = Round.objects.filter(game=game).filter(active=True)
    if len(rounds) == 0:
        return render_to_string('finalRoundError.md')
    round = rounds[0]

    roundResults = RoundResult.objects.filter(round=round)
    i=0
    results=[]    
    for name in names:
        for roundResult in roundResults:
            if roundResult.jugador == name:
                result={}
                result['name'] = name
                result['score'] = roundResult.score
                results.append(result)
                i+=1
                break
    results = sorted(results, key=lambda k: k['score']) 
    if i == len(names):
        Round.objects.filter(id=round.id).update(active=False)
        r = round_array.index(round.rounds)
        if r == 7:
            return render_to_string('finalRound.md', {'results': results})
        else:
            nextRound = Round(game=game, rounds=round_array[r+1])
            nextRound.save()
            return render_to_string('nextRound.md', {'round': nextRound, 'results': results})
    else:
        return render_to_string('nextRoundError.md')
            


def _display_add_score(chat_id, name, scores):

    if len(scores) > 3:
        score = parse_add_result(scores)
    else:
        try:
            score = int(scores)
        except ValueError:
            return render_to_string('scoreError.md')

    if score == -1:
        return render_to_string('scoreError.md')

    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')

    game = games[0]
    names = game.jugadores.split(',')
    inGame = False
    for n in names:
        if name == n:
            inGame=True
            break
    if inGame:
        rounds = Round.objects.filter(game=game).filter(active=True)

        
        round = rounds[0]
        roundResult = RoundResult(round=round, jugador=name, score=score)
        roundResult.save()
        gameResults = GameResult.objects.filter(game=game).filter(jugador=name)

        if len(gameResults) == 0:
            gameResult = GameResult(game=game, jugador=name, score=score)
            gameResult.save()
        else:
            gameResults[0].score = gameResults[0].score + score
            gameResults[0].save()

        return render_to_string('addScore.md', {'name': name, 'score': score})
    else:
        return render_to_string('noPlayerInGame.md', {'name': name})

def _display_scores(chat_id):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')
    game = games[0]

    gameResults = GameResult.objects.filter(game=game)
    if gameResults == 0:
        return render_to_string('noScoresYet.md')
    results=[]
    for gameResult in gameResults:
        result={}
        result['name'] = gameResult.jugador
        result['score'] = gameResult.score
        results.append(result)
    results = sorted(results, key=lambda k: k['score']) 

    return render_to_string('scores.md', {'results': results})

def _display_end_game(chat_id):
    games = Game.objects.filter(chat=chat_id).filter(active=True)
    if len(games) == 0:
        return render_to_string('noGameError.md')
    game = games[0]
    gameResults = GameResult.objects.filter(game=game)
    if gameResults == 0:
        return render_to_string('noScoresGame.md')
    results=[]
    for gameResult in gameResults:
        result={}
        result['name'] = gameResult.jugador
        result['score'] = gameResult.score
        results.append(result)
    results = sorted(results, key=lambda k: k['score']) 

    game.active = False
    game.save()

    return render_to_string('finalScores.md', {'results': results})

class CommandReceiveView(View):
    def post(self, request, bot_token):
        if bot_token != settings.TELEGRAM_BOT_TOKEN:
            return HttpResponseForbidden('Invalid token')

        commands = {
            '/start': _display_help,
            '/help': _display_help,
            '/newGame': _display_new_game,
            '/addPlayer': _display_add_player,
            '/deletePlayer': _display_delete_player,
            '/players': _display_players,
            '/startGame': _display_start_game,            
            '/round': _display_actual_round,
            '/nextRound': _display_next_round,
            '/addScore': _display_add_score,
            '/scores': _display_scores,
            '/endGame': _display_end_game,
        }

        raw = request.body.decode('utf-8')
        logger.info(raw)

        try:
            payload = json.loads(raw)
        except ValueError:
            return HttpResponseBadRequest('Invalid request body')
        else:
            chat_id = payload['message']['chat']['id']
            cmd = payload['message'].get('text')  # command

            msg = cmd.split()
            func = commands.get(msg[0])
            param1=''
            param2=''        

            if func:
                try:
                    if len(msg) == 1:
                        TelegramBot.sendMessage(chat_id, func(chat_id), parse_mode='Markdown')
                    elif len(msg) == 2:
                        param1 = cmd.split()[1]
                        TelegramBot.sendMessage(chat_id, func(chat_id,param1), parse_mode='Markdown')
                    elif len(msg) == 3:
                        param1 = cmd.split()[1]
                        param2 = cmd.split()[2]
                        TelegramBot.sendMessage(chat_id, func(chat_id,param1,param2), parse_mode='Markdown')
                    else:
                        TelegramBot.sendMessage(chat_id, 'Too many params!')
                except TypeError:
                    TelegramBot.sendMessage(chat_id, 'Wrong number of params!')
                
            else:
                TelegramBot.sendMessage(chat_id, 'I do not understand you!')

        return JsonResponse({}, status=200)

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(CommandReceiveView, self).dispatch(request, *args, **kwargs)
