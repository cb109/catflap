from datetime import datetime, timedelta
from typing import Union

import pendulum
from django.conf import settings
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from server.catflap.models import CatFlap, ManualStatusUpdate

COOKIE_NAME_CATFLAP_UUID = "catflap_uuid"


def get_localtime_now():
    now = timezone.now()
    return timezone.localtime(now)


def get_pendulum_now():
    """Timezone does not matter here, we just use this to compute relative offsets."""
    return pendulum.now()


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


def get_inside_outside_statistics(catflap, num_days_ago: Union[int, float] = 7):
    pendulum_now = get_pendulum_now()  # Just used to compute relative durations.
    now = get_localtime_now()
    days_ago = now - timedelta(days=num_days_ago)

    ranges = []
    samples = get_inside_outside_samples_since(catflap, days_ago)

    next_cat_inside = catflap.cat_inside
    end = now
    current_range = {"start": None, "end": end, "inside": next_cat_inside}

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

    last_range = {"start": days_ago, "end": end, "inside": next_cat_inside}
    ranges.insert(0, last_range)

    seconds_inside = 0
    seconds_outside = 0

    series = []
    durations = []

    for timerange in ranges:
        range_start = timezone.localtime(timerange["start"])
        range_end = timezone.localtime(timerange["end"])

        formatted_start = range_start.isoformat()
        formatted_end = range_end.isoformat()

        inside = timerange["inside"]
        category = "In" if inside else "Out"
        fill_color = settings.COLOR_INSIDE if inside else settings.COLOR_OUTSIDE

        seconds_taken = (range_end - range_start).total_seconds()
        duration_in_words = shorten_pendulum_duration_string(
            (
                pendulum_now - pendulum_now.subtract(hours=seconds_taken / 60 / 60)
            ).in_words()
        )
        durations.append(duration_in_words)

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

    return series, durations, seconds_inside, seconds_outside


@require_http_methods(["GET"])
def get_catflap_status(request, catflap_uuid):
    days = float(request.GET.get("days", "0.5").replace(",", "."))
    if days > 14:
        raise ValidationError("Looking back more than 14 days back is not allowed")

    catflap = CatFlap.objects.get(uuid=catflap_uuid)

    series, durations, seconds_inside, seconds_outside = get_inside_outside_statistics(
        catflap, num_days_ago=days
    )
    seconds_total = seconds_inside + seconds_outside
    ratio_inside = seconds_inside / (seconds_total / 100.0)
    ratio_outside = seconds_outside / (seconds_total / 100.0)
    pendulum_now = get_pendulum_now()
    total_inside_in_words = shorten_pendulum_duration_string(
        (
            pendulum_now - pendulum_now.subtract(hours=seconds_inside / 60 / 60)
        ).in_words()
    )
    total_outside_in_words = shorten_pendulum_duration_string(
        (
            pendulum_now - pendulum_now.subtract(hours=seconds_outside / 60 / 60)
        ).in_words()
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
        {"label": "2 hours", "days": 0.08333},
        {"label": "4 hours", "days": 0.16666},
        {"label": "8 hours", "days": 0.33333},
        {"label": "12 hours", "days": 0.5},
        {"label": "24 hours", "days": 1},
        {"label": "2 days", "days": 2},
        {"label": "3 days", "days": 3},
        {"label": "1 week", "days": 7},
        {"label": "2 weeks", "days": 14},
    ]
    response = render(
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
                "durations": durations,
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
    return response


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
