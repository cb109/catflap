from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CatFlap(BaseModel):
    """A device with sensors to detect movement events."""

    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Event(BaseModel):
    """A movement event on a Catflap device."""

    catflap = models.ForeignKey("catflap.CatFlap", on_delete=models.CASCADE)

    class Kinds(models.TextChoices):
        CLOSED = "CL"
        OPENED_INWARD = "OI"
        OPENED_OUTWARD = "OO"

    kind = models.CharField(
        max_length=2,
        choices=Kinds.choices,
    )

    def __str__(self):
        return f"{self.created_at} {self.catflap.name} {self.kind}"

