The results of the round are:
{% for result in results %}[{{ result.name }}]: *{{ result.score }}*
{% endfor %}
That was the last round!
End the game and see the results with */endGame*