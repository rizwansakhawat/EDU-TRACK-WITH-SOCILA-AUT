from django import models


class Institute(models.Model):
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name