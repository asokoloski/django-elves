from django.views.static import serve
from django.template import Context, Template

def serve_rendered(request, path, document_root=None, show_indexes=False):
    response = serve(request, path, document_root, show_indexes)
    response.content = Template(response.content).render(Context({'request': request}))
    return response
