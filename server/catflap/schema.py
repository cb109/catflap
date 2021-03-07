import graphene
from graphene_django import DjangoObjectType

from server.catflap.models import CatFlap, Event


class CatFlapType(DjangoObjectType):
    class Meta:
        model = CatFlap
        fields = (
            "id",
            "name",
        )


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        fields = (
            "catflap",
            "created_at",
            "id",
            "kind",
        )


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
        return Event.objects.filter(
            catflap__name=name
        ).order_by("-created_at")


class Mutation(graphene.ObjectType):
    create_event = EventMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
