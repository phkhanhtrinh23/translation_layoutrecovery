from django.db import models
from account.models import User


# Create your models here.
class PDF(models.Model):
    pdf_id = models.AutoField(primary_key=True)
    owner_id = models.ForeignKey(
        User, to_field="user_id", related_name="owner_id", on_delete=models.CASCADE
    )
    file_name = models.CharField(max_length=100)
    file = models.FileField(upload_to="PDFs/", default="PDFs/sample.pdf")
    language = models.CharField(max_length=2, default="en")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

    def isOwner(self, id):
        return self.owner_id.user_id == id

    def save_update(self):
        super(PDF, self).save()

    def changeOwner(self, new_owner):
        self.owner_id = new_owner
        self.save_update()

    def updateLanguage(self, new_language):
        self.language = new_language
        self.save_update()

    def getLanguage(self):
        return self.language

    def getOwner(self):
        return self.owner_id.user_id


class Translation(models.Model):
    translation_id = models.AutoField(primary_key=True)
    status = models.IntegerField(default=0)  # 0: processing, 1: success, -1: failure
    file_input = models.ForeignKey(
        PDF, related_name="file_input", on_delete=models.CASCADE
    )
    file_output = models.ForeignKey(
        PDF, related_name="output", on_delete=models.CASCADE
    )
    time_stamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.transaction_id)

    def getFileInputName(self):
        return self.file_input.file_name

    def getFileOutputName(self):
        return self.file_output.file_name
    
    def getFileInput(self):
        return self.file_input
    
    def getFileOutput(self):
        return self.file_output

    def getStatus(self):
        return self.status

    def getTranslationData(self):
        return (
            str(self.file_input),
            str(self.file_output),
            self.file_input.getOwner(),
            self.status,
        )

    def isAbleToUpdate(self):
        return self.status != 0

    def save_update(self):
        super(PDF, self).save()

    def updateStatus(self, new_status):
        self.status = new_status
        self.save_update()

    def updateFileOutput(self, new_file_output):
        self.file_output = new_file_output
        self.save_update()


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        User, to_field="user_id", related_name="user_id_f", on_delete=models.CASCADE
    )
    translation_id = models.ForeignKey(
        Translation, to_field="translation_id", related_name="translation_id_f", on_delete=models.CASCADE
    )
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.pdf_id.pdf_id + " " + str(self.rating)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "translation_id"], name="unique_feedback"
            )
        ]
