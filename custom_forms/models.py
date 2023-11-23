from djongo import models


class FieldTemplate(models.Model):
    class FieldType(models.TextChoices):
        PHONE_NUMBER = 'PN', 'Phone Number'
        EMAIL = 'EM', 'Email'
        TEXT = 'TX', 'Text'
        DATE = 'DT', 'Date'

    f_name = models.CharField(max_length=255, primary_key=True)
    f_type = models.CharField(max_length=2,
                              choices=FieldType.choices)

    class Meta:
        managed = False


class CustomForm(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    fields = models.ArrayField(
        model_container=FieldTemplate
    )

    objects = models.DjongoManager()
