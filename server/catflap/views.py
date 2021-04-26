from datetime import datetime, timedelta

import pendulum
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from server.catflap.models import CatFlap, ManualStatusUpdate


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
    event_values = catflap.events.filter(created_at__gte=threshold).values(
        "created_at",
    )

    update_values = ManualStatusUpdate.objects.filter(
        catflap=catflap, created_at__gte=threshold
    ).values(
        "created_at",
        "cat_inside",
    )

    all_values = sorted(
        list(event_values) + list(update_values),
        key=lambda item: item["created_at"],
        reverse=True,
    )
    return all_values


def get_inside_outside_statistics(catflap, num_days_ago=7):
    now = timezone.localtime()
    days_ago = now - timedelta(days=num_days_ago)

    ranges = []
    samples = get_inside_outside_samples_since(catflap, days_ago)

    next_cat_inside = catflap.cat_inside
    current_range = {"start": None, "end": now, "inside": next_cat_inside}

    for sample in samples:
        cat_inside = sample.get("cat_inside", None)
        is_manual_update = cat_inside is not None

        end = sample["created_at"]
        current_range["start"] = end
        ranges.insert(0, current_range)

        if is_manual_update:
            next_cat_inside = not cat_inside
        else:
            next_cat_inside = not next_cat_inside

        current_range = {"start": None, "end": end, "inside": next_cat_inside}

    last_range = {"start": days_ago, "end": end, "inside": not next_cat_inside}
    ranges.insert(0, last_range)

    seconds_inside = 0
    seconds_outside = 0

    series = []
    for timerange in ranges:
        range_start = timezone.localtime(timerange["start"])
        range_end = timezone.localtime(timerange["end"])

        formatted_start = range_start.isoformat()
        formatted_end = range_end.isoformat()

        inside = timerange["inside"]
        category = "Inside" if inside else "Outside"
        fill_color = settings.COLOR_INSIDE if inside else settings.COLOR_OUTSIDE

        seconds_taken = (range_end - range_start).total_seconds()
        if inside:
            seconds_inside += seconds_taken
        else:
            seconds_outside += seconds_taken

        series.append(
            {
                "x": category,
                "y": [formatted_start, formatted_end],
                "fillColor": fill_color,
            }
        )

    return series, seconds_inside, seconds_outside


@require_http_methods(["GET"])
def get_catflap_status(request, catflap_uuid):
    days = int(request.GET.get("days", "1"))
    if days > 14:
        raise ValidationError("Looking back more than 14 days back is not allowed")

    catflap = CatFlap.objects.get(uuid=catflap_uuid)

    series, seconds_inside, seconds_outside = get_inside_outside_statistics(
        catflap, num_days_ago=days
    )
    seconds_total = seconds_inside + seconds_outside
    ratio_inside = seconds_inside / (seconds_total / 100.0)
    ratio_outside = seconds_outside / (seconds_total / 100.0)
    now = pendulum.now()
    total_inside_in_words = shorten_pendulum_duration_string(
        (now - now.subtract(hours=seconds_inside / 60 / 60)).in_words()
    )
    total_outside_in_words = shorten_pendulum_duration_string(
        (now - now.subtract(hours=seconds_outside / 60 / 60)).in_words()
    )

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
    dayfilters = [
        {"label": "24h", "days": 1},
        {"label": "2d", "days": 2},
        {"label": "3d", "days": 3},
        {"label": "1w", "days": 7},
        {"label": "2w", "days": 14},
    ]
    return render(
        request,
        "status.html",
        {
            "cat_picture_location_url": cat_picture_location_url,
            "cat_picture_url": settings.PICTURE_URL_CAT,
            "catflap": catflap,
            "color_inside": settings.COLOR_INSIDE,
            "color_outside": settings.COLOR_OUTSIDE,
            "dayfilters": dayfilters,
            "days": days,
            "statistics": {
                "ratio_inside": ratio_inside,
                "ratio_outside": ratio_outside,
                "series": series,
                "total_inside_in_words": total_inside_in_words,
                "total_outside_in_words": total_outside_in_words,
            },
            "set_inside_url": set_inside_url,
            "set_outside_url": set_outside_url,
        },
    )


def shorten_pendulum_duration_string(duration_str):
    return (
        duration_str.replace(" days", "d")
        .replace(" day", "d")
        .replace(" hours", "h")
        .replace(" hour", "h")
        .replace(" minutes", "m")
        .replace(" minute", "m")
        .replace(" seconds", "s")
        .replace(" second", "s")
    )
