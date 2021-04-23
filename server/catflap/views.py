from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from server.catflap.models import CatFlap, ManualStatusUpdate


def track_manual_intervention(catflap, cat_inside):
    ManualStatusUpdate.objects.create(
        catflap=catflap,
        cat_inside=catflap.cat_inside,
    )


@require_http_methods(["GET"])
def set_catflap_cat_inside(request, catflap_uuid):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(uuid=catflap_uuid)
    if not catflap.cat_inside:
        catflap.cat_inside = True
        catflap.save()
        track_manual_intervention(catflap, cat_inside=True)
    return redirect("status", catflap_uuid=catflap_uuid)


@require_http_methods(["GET"])
def set_catflap_cat_outside(request, catflap_uuid):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(uuid=catflap_uuid)
    if catflap.cat_inside:
        catflap.cat_inside = False
        catflap.save()
        track_manual_intervention(catflap, cat_inside=False)
    return redirect("status", catflap_uuid=catflap_uuid)


@require_http_methods(["GET"])
def get_catflap_status(request, catflap_uuid):
    catflap = CatFlap.objects.get(uuid=catflap_uuid)
    location = "inside" if catflap.cat_inside else "outside"
    return HttpResponse(f"{catflap.cat_name} is likely {location}")
