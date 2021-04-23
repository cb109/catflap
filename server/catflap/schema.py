import graphene
import pendulum
from django.conf import settings
from django.urls import reverse
from graphene_django import DjangoObjectType
from server.catflap.models import CatFlap, Event
from server.catflap.push import send_push_notification


class CatFlapType(DjangoObjectType):
    class Meta:
        model = CatFlap
        fields = (
            "id",
            "name",
        )


class EventType(DjangoObjectType):
    kind_label = graphene.String(source="kind_label")

    class Meta:
        model = Event
        fields = (
            "catflap",
            "created_at",
            "id",
            "kind_label",
            "kind",
        )


def notify_user(catflap, event):
    located_at = "inside" if catflap.cat_inside else "outside"
    current_url = settings.NOTIFICATION_BASE_URL + reverse(
        f"set-{located_at}", args=(catflap.id,)
    )

    inverse_located_at = "inside" if located_at == "outside" else "outside"
    inverse_url = settings.NOTIFICATION_BASE_URL + reverse(
        f"set-{inverse_located_at}", args=(catflap.id,)
    )

    duration_str = ""
    previous_event = event.get_previous_by_created_at()
    if previous_event:
        duration = pendulum.instance(event.created_at) - pendulum.instance(
            previous_event.created_at
        )
        duration_str = (
            f" (after {duration.in_words()})".replace("days", "d")
            .replace("hours", "h")
            .replace("minutes", "m")
            .replace("seconds", "s")
        )

    title = f"{catflap.cat_name} is {located_at} now{duration_str}"
    message = (
        f"{catflap.name} {event.kind_label}: {catflap.cat_name} is likely "
        f"<b>{located_at}</b> now.\n\n"
        f"Wrong? Set location manually here: {catflap.cat_name} is "
        f"<a href='{inverse_url}'>{inverse_located_at}</a> / "
        f"<a href='{current_url}'>{located_at}</a>"
    )
    send_push_notification(message, title=title)


class EventMutation(graphene.Mutation):
    class Arguments:
        catflap_id = graphene.Int(required=True)
        kind = graphene.String(required=True)

    event = graphene.Field(EventType)

    @classmethod
    def mutate(cls, root, info, catflap_id, kind):
        catflap = CatFlap.objects.get(id=catflap_id)
        event = Event(catflap=catflap, kind=kind)
        event.full_clean()
        event.save()

        catflap.cat_inside = not catflap.cat_inside
        catflap.save()

        notify_user(catflap, event)

        return EventMutation(event=event)


class Query(graphene.ObjectType):
    all_catflaps = graphene.List(CatFlapType)
    all_events = graphene.List(EventType)

    events_by_catflap_name = graphene.List(
        EventType, name=graphene.String(required=True)
    )

    def resolve_all_catflaps(root, info):
        return CatFlap.objects.all()

    def resolve_all_events(root, info):
        return Event.objects.all()

    def resolve_events_by_catflap_name(root, info, name):
        return Event.objects.filter(catflap__name=name).order_by("-created_at")


class Mutation(graphene.ObjectType):
    create_event = EventMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
