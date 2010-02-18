from django.http import HttpResponse

from django.template import Template, Context

TEMP = Template('''
<html>
<head><title>Sprite Test Page</title></head>
<body>
<table>
{% for name, cs in images %}
<tr>
<td>
{{ name }}
</td>
<td style="padding: 10px; background-color: #EEE">
<div style="background-color: white; float: left; {% sprite name %} width: {{ cs.size.0 }}px; height: {{ cs.size.1 }}px;">
&nbsp;
</div>
</td></tr>
{% endfor %}
</table>
</body>
</html>
''')

def all_sprites(request):
    from django_elves.compiler import sprite_manager
    sprite_manager.force_import()

    images = []
    for name, cs in sprite_manager.table().iteritems():
        images.append((name, cs))

    con = {'images': images}
    return HttpResponse(TEMP.render(Context(con)))
