from datetime import datetime, timezone
from django.db import models


class Applicant(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.FileField(upload_to="llm_note/", default="llm_note/default_note.txt")

    class Meta:
        db_table = "llm_file"
