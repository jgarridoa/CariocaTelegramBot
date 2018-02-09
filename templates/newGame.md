*Welcome to a new game of Carioca*

This game is played in: *{{lugar}} *
Date: *{{date|date:"d/F/Y"}}*

The players are: 
{% for item in items %} Player [{{ item.number }}]: *{{ item.name }}*
{% endfor %}


