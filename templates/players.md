The players in this game are: 
{% for item in items %} Player [{{ item.number }}]: *{{ item.name }}*
{% endfor %}