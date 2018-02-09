The final results are:
{% for result in results %}{% if forloop.first %}The winner is: *{{ result.name }}* with *{{ result.score }}* points.
{% elif forloop.last %}
But everybody knows the real winner is *{{ result.name }}* with *{{ result.score }}* points
{% else %}*{{ forloop.counter }} place* is *{{ result.name }}* with *{{ result.score }}* points{% endif %}{% endfor %}
Thanks for using this bot for your game! :D