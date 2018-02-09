from django.db import models

# Create your models here.

class Game(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    lugar = models.CharField(max_length=200)
    jugadores = models.TextField()
    chat = models.CharField(max_length=20)
    active = models.BooleanField(default=True)
    start = models.BooleanField(default=False)

class Round(models.Model):
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
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    rounds = models.CharField(max_length=4, choices=ROUNDS)
    active = models.BooleanField(default=True)
    

class GameResult(models.Model):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    jugador = models.CharField(max_length=15)
    score = models.IntegerField()

class RoundResult(models.Model):
    round = models.ForeignKey('Round', on_delete=models.CASCADE)
    jugador = models.CharField(max_length=15)
    score = models.IntegerField()
