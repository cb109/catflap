import uuid

from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CatFlap(BaseModel):
    """A device with sensors to detect movement events."""

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=64)
    cat_name = models.CharField(max_length=64, default="Cat")
    cat_inside = models.BooleanField(default=True)

    @property
    def cat_location(self):
        return describe_location(self.cat_inside)

    def __str__(self):
        return self.name


class Event(BaseModel):
    """A movement event on a Catflap device."""

    catflap = models.ForeignKey(
        "catflap.CatFlap", on_delete=models.CASCADE, related_name="events"
    )

    class Kinds(models.TextChoices):
        OPENED_CLOSED = "OC"

    kind = models.CharField(
        max_length=2,
        choices=Kinds.choices,
    )

    @property
    def kind_label(self):
        return self.Kinds(self.kind).name.replace("_", " ").capitalize()

    def __str__(self):
        return f"{self.created_at} {self.catflap.name} {self.kind}"


class ManualStatusUpdate(BaseModel):
    """Someone changed the cat_inside status to correct it."""

    catflap = models.ForeignKey("catflap.CatFlap", on_delete=models.CASCADE)
    cat_inside = models.BooleanField()

    @property
    def cat_location(self):
        return describe_location(self.cat_inside)

    def __str__(self):
        return f"{self.catflap.name} -> {self.cat_location}"


def describe_location(cat_inside):
    return "inside" if cat_inside else "outside"
