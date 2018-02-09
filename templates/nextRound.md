The results of the round are:
{% for result in results %}[{{ result.name }}]: *{{ result.score }}*
{% endfor %}
The next round *{{ round.get_rounds_display }}* is starting!