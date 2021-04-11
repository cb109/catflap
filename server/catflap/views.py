from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from server.catflap.models import CatFlap


@require_http_methods(["GET"])
def set_catflap_cat_inside(request, catflap_id):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(id=catflap_id)
    catflap.cat_inside = True
    catflap.save()
    return HttpResponse(f"{catflap.cat_name} location updated: inside")


@require_http_methods(["GET"])
def set_catflap_cat_outside(request, catflap_id):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(id=catflap_id)
    catflap.cat_inside = False
    catflap.save()
    return HttpResponse(f"{catflap.cat_name} location updated: outside")
