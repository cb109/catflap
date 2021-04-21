from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from server.catflap.models import CatFlap


@require_http_methods(["GET"])
def set_catflap_cat_inside(request, catflap_id):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(id=catflap_id)
    catflap.cat_inside = True
    catflap.save()
    return redirect("status", catflap_id=catflap_id)


@require_http_methods(["GET"])
def set_catflap_cat_outside(request, catflap_id):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(id=catflap_id)
    catflap.cat_inside = False
    catflap.save()
    return redirect("status", catflap_id=catflap_id)


@require_http_methods(["GET"])
def get_catflap_status(request, catflap_id):
    catflap = CatFlap.objects.get(id=catflap_id)
    location = "inside" if catflap.cat_inside else "outside"
    return HttpResponse(f"{catflap.cat_name} is likely {location}")

