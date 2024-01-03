from django.http import HttpResponse
from django.views.decorators.http import require_GET

@require_GET
def robots_txt(request):
    lines = [
        "User-Agent: *",
        "Disallow: /static/",
        "Disallow: /admin/",
        "Disallow: /files/",
        "Disallow: /workspaces/",
        "Disallow: /new/",
        "Disallow: /ajax/",
        "Disallow: /webhooks/",
        "Disallow: /documents/",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

