from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from server.catflap.models import CatFlap, ManualStatusUpdate

APEXCHARTS_RANGEBAR_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def track_manual_intervention(catflap, cat_inside):
    ManualStatusUpdate.objects.create(
        catflap=catflap,
        cat_inside=catflap.cat_inside,
    )


def redirect_to_status_page(request, catflap_uuid):
    days = request.GET.get("days")
    url = reverse("status", kwargs={"catflap_uuid": catflap_uuid}) + (
        f"?days={days}" if days else ""
    )
    return redirect(url)


@require_http_methods(["GET"])
def set_catflap_cat_inside(request, catflap_uuid):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(uuid=catflap_uuid)
    if not catflap.cat_inside:
        catflap.cat_inside = True
        catflap.save()
        track_manual_intervention(catflap, cat_inside=True)

    return redirect_to_status_page(request, catflap_uuid)


@require_http_methods(["GET"])
def set_catflap_cat_outside(request, catflap_uuid):
    """GET so it can be used as an email link."""
    catflap = CatFlap.objects.get(uuid=catflap_uuid)
    if catflap.cat_inside:
        catflap.cat_inside = False
        catflap.save()
        track_manual_intervention(catflap, cat_inside=False)

    return redirect_to_status_page(request, catflap_uuid)


def get_inside_outside_samples_since(catflap: CatFlap, threshold: datetime) -> list:
    event_values = catflap.events.filter(created_at__gte=threshold).values("created_at")

    # update_values = ManualStatusUpdate.objects.filter(
    #     catflap=catflap, created_at__gte=threshold
    # ).values("created_at", "cat_inside")

    update_values = []

    all_values = sorted(
        list(event_values) + list(update_values),
        key=lambda item: item["created_at"],
        reverse=True,
    )
    return all_values


def get_inside_outside_series(catflap, num_days_ago=7):
    now = datetime.now(timezone.utc)  # Avoid offset-naive VS offset-aware error.
    days_ago = now - timedelta(days=num_days_ago)

    ranges = []
    samples = get_inside_outside_samples_since(catflap, days_ago)

    current_cat_inside = catflap.cat_inside
    current_range = {"start": None, "end": now, "inside": current_cat_inside}

    for sample in samples:
        end = sample["created_at"]
        current_range["start"] = end
        ranges.insert(0, current_range)

        current_cat_inside = not current_cat_inside
        current_range = {"start": None, "end": end, "inside": current_cat_inside}

    last_range = {"start": days_ago, "end": end, "inside": not current_cat_inside}
    ranges.insert(0, last_range)

    series = []
    for timerange in ranges:
        range_start = timerange["start"].strftime(APEXCHARTS_RANGEBAR_DATETIME_FORMAT)
        range_end = timerange["end"].strftime(APEXCHARTS_RANGEBAR_DATETIME_FORMAT)

        inside = timerange["inside"]
        category = "Inside" if inside else "Outside"
        fill_color = "#48c774" if inside else "#f14668"

        series.append(
            {
                "x": category,
                "y": [range_start, range_end],
                "fillColor": fill_color,
            }
        )

    return series


@require_http_methods(["GET"])
def get_catflap_status(request, catflap_uuid):
    days = int(request.GET.get("days", "1"))
    if days > 14:
        raise ValidationError("Looking back more than 14 days back is not allowed")

    catflap = CatFlap.objects.get(uuid=catflap_uuid)

    apexcharts_series = get_inside_outside_series(catflap, num_days_ago=days)

    set_inside_url = settings.NOTIFICATION_BASE_URL + reverse(
        "set-inside", args=(catflap_uuid,)
    )
    set_outside_url = settings.NOTIFICATION_BASE_URL + reverse(
        "set-outside", args=(catflap_uuid,)
    )
    cat_picture_location_url = (
        settings.PICTURE_URL_CAT_INSIDE
        if catflap.cat_inside
        else settings.PICTURE_URL_CAT_OUTSIDE
    )
    return render(
        request,
        "status.html",
        {
            "cat_picture_location_url": cat_picture_location_url,
            "cat_picture_url": settings.PICTURE_URL_CAT,
            "catflap": catflap,
            "days": days,
            "series": apexcharts_series,
            "set_inside_url": set_inside_url,
            "set_outside_url": set_outside_url,
        },
    )
