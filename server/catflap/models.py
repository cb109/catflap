from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CatFlap(BaseModel):
    """A device with sensors to detect movement events."""

    name = models.CharField(max_length=64)
    cat_name = models.CharField(max_length=64, default="Cat")
    cat_inside = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Event(BaseModel):
    """A movement event on a Catflap device."""

    catflap = models.ForeignKey("catflap.CatFlap", on_delete=models.CASCADE)

    class Kinds(models.TextChoices):
        CLOSED = "CL"
        OPENED = "O"
        OPENED_CLOSED = "OC"
        OPENED_INWARD = "OI"
        OPENED_OUTWARD = "OO"

    kind = models.CharField(max_length=2, choices=Kinds.choices,)

    @property
    def kind_label(self):
        return self.Kinds(self.kind).name.replace("_", " ").capitalize()

    def __str__(self):
        return f"{self.created_at} {self.catflap.name} {self.kind}"


class ManualStatusUpdate(BaseModel):
    """Someone changed the cat_inside status to correct it."""

    catflap = models.ForeignKey("catflap.CatFlap", on_delete=models.CASCADE)
    cat_inside = models.BooleanField()

    def __str__(self):
        location = "inside" if self.cat_inside else "outside"
        return f"{self.catflap.name} -> {location}"

