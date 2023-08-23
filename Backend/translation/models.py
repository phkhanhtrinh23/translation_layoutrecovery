from django.db import models
from account.models import User


class PDF(models.Model):
    pdf_id = models.AutoField(primary_key=True, unique=True)
    owner_id = models.ForeignKey(
        User, to_field="user_id", related_name="owner_id", on_delete=models.CASCADE
    )
    file_name = models.CharField(max_length=255, blank=True)
    file = models.CharField(
        max_length=255,
        default="https://storage.googleapis.com/avatar-a0439.appspot.com/sample.pdf",
    )
    language = models.CharField(max_length=2, default="en")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

    def save(self, *args, **kwargs):
        """
        Save the object to the database.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if not self.pdf_id:
            last_pdf = PDF.objects.last()
            last_id = last_pdf.pdf_id if last_pdf else 0
            self.pdf_id = last_id + 1
        if not self.file_name:
            self.file_name = str(self.file).split("/")[-1]
            print(self.file_name)
        super().save(*args, **kwargs)

    def save_update(self):
        """
        Saves the current object and updates the database.
        """
        super(PDF, self).save()

    def changeOwner(self, new_owner):
        """
        Change the owner of the object to the specified new owner.

        Args:
            new_owner (str): The ID of the new owner.

        Returns:
            None
        """
        self.owner_id = new_owner
        self.save_update()

    def updateLanguage(self, new_language):
        """
        Update the language of the object.
        """
        self.language = new_language
        self.save_update()

    def getLanguage(self):
        """
        Get the language of the object.
        """
        return self.language

    def getOwner(self):
        """
        Get the owner of the object.
        """
        return self.owner_id.user_id

    def getFileUrl(self):
        """
        Get the file URL of the object.
        """
        return self.file


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
        """
        Get the file input name.
        """
        return str(self.file_input)

    def getFileOutputName(self):
        """
        Get the file output name.
        """
        return str(self.file_output)

    def getFileInput(self):
        """
        Get the file input.
        """
        return self.file_input

    def getFileOutput(self):
        """
        Get the file output.
        """
        return self.file_output

    def getStatus(self):
        """
        Get the status.
        """
        return self.status

    def getTranslationData(self):
        """
        Get the translation data.
        """
        return (
            str(self.file_input),
            str(self.file_output),
            self.file_input.getOwner(),
            self.status,
        )

    def isAbleToUpdate(self):
        """
        Check if the translation is able to be updated.
        """
        return self.status != 0

    def save_update(self):
        """
        Saves the current object and updates the database.
        """
        super(PDF, self).save()

    def updateStatus(self, new_status):
        """
        Updates the status of the object.

        Parameters:
            new_status (any): The new status to be assigned.

        Returns:
            None
        """
        self.status = new_status
        self.save_update()

    def updateFileOutput(self, new_file_output):
        """
        Updates the file output of the object.

        Args:
            new_file_output (str): The new file output to set.

        Returns:
            None
        """
        self.file_output = new_file_output
        self.save_update()


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        User, to_field="user_id", related_name="user_id_f", on_delete=models.CASCADE
    )
    translation_id = models.ForeignKey(
        Translation,
        to_field="translation_id",
        related_name="translation_id_f",
        on_delete=models.CASCADE,
    )
    rating = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user_id) + " " + str(self.rating)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "translation_id"], name="unique_feedback"
            )
        ]
