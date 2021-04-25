from datetime import datetime, timedelta

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
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
    set_inside_url = settings.NOTIFICATION_BASE_URL + reverse(
        "set-inside", args=(catflap_uuid,)
    )
    set_outside_url = settings.NOTIFICATION_BASE_URL + reverse(
        "set-outside", args=(catflap_uuid,)
    )
    return render(
        request,
        "status.html",
        {
            "cat_picture_url": settings.CAT_PICTURE_URL,
            "catflap": catflap,
            "set_inside_url": set_inside_url,
            "set_outside_url": set_outside_url,
        },
    )
