import os
from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password


def isAbleToUpdatePassword(self, new_password):
    """
    Checks if the given new password is able to be updated for the current user.

    Parameters:
        self (obj): The current object instance.
        new_password (str): The new password to be checked.

    Returns:
        bool: True if the new password is able to be updated, False otherwise.
    """
    return (
        new_password != self.password
        and new_password != ""
        and len(new_password) >= 6
        and len(new_password) <= 64
    )


def hash_password(password):
    """
    Hashes a password using the make_password function from django.contrib.auth.hashers.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return make_password(password)


class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True, unique=True)
    full_name = models.CharField(max_length=255, blank=False)
    bio = models.CharField(max_length=255, blank=True)
    avatar = models.CharField(
        max_length=255,
        default="https://storage.googleapis.com/avatar-a0439.appspot.com/avatar.png",
    )

    def __str__(self):
        return str(self.profile_id)

    def save(self, *args, **kwargs):
        """
        Save the object to the database.

        This method overrides the save method of the parent class and adds functionality to automatically assign a profile ID if it is not already set. 

        Parameters:
            *args: Additional positional arguments that are passed to the parent save method.
            **kwargs: Additional keyword arguments that are passed to the parent save method.

        Returns:
            None
        """
        if not self.profile_id:
            last_profile = Profile.objects.last()
            last_id = last_profile.profile_id if last_profile else 0
            self.profile_id = last_id + 1
        super().save(*args, **kwargs)

    def getFullName(self):
        """
        Returns the full name of the user.
        """
        return str(self.full_name)

    def updateName(self, full_name):
        """
        Updates the name of the profile.

        Args:
            full_name (str): The new full name for the profile.

        Returns:
            bool: True if the name was updated successfully, False otherwise.
        """
        if full_name != "":
            self.full_name = full_name
            super(Profile, self).save()
            return True
        else:
            return False

    def updateBio(self, bio):
        """
        Updates the bio of the profile.

        Parameters:
            bio (str): The new bio for the profile.

        Returns:
            bool: True if the bio is updated and saved successfully, False otherwise.
        """
        if bio != "":
            self.bio = bio
            super(Profile, self).save()
            return True
        else:
            return False

    def updateAvatar(self, avatar):
        """
        Updates the avatar of the profile.

        Parameters:
            avatar (None or str): The new avatar for the profile. If None, no avatar is set.

        Returns:
            bool: True if the avatar was updated successfully, False otherwise.
        """
        if avatar != None:
            self.avatar = avatar
            super(Profile, self).save()
            return True
        else:
            return False

    def getProfileData(self):
        """
        Returns the full name, bio, and avatar of the profile.
        """
        return str(self.full_name), str(self.bio), self.avatar


class User(models.Model):
    user_id = models.AutoField(primary_key=True, unique=True)
    username = models.CharField(max_length=255, blank=False, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True, blank=True)
    profile = models.ForeignKey(
        Profile, to_field="profile_id", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        """
        Saves the object to the database.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            None
        """
        if not self.user_id:
            last_user = User.objects.last()
            last_id = last_user.user_id if last_user else 0
            self.user_id = last_id + 1
        super().save(*args, **kwargs)

    def isAuthenticated(self, username, password):
        """
        Checks if the given username and password are valid.
        """
        return username == self.username and check_password(password, self.password)

    def getProfileId(self):
        """
        Returns the profile ID of the user.
        """
        return str(self.profile_id)

    def updatePassword(self, new_password):
        """
        Updates the password for the user.

        Parameters:
            new_password (str): The new password to be set for the user.

        Returns:
            bool: True if the password was updated successfully, False otherwise.
        """
        if isAbleToUpdatePassword(self, new_password):
            self.password = hash_password(new_password)
            return True
        return False

    def getUserData(self):
        """
        Returns the username, email, full name, bio, date joined, and avatar of the user.
        """
        full_name, bio, avatar = self.profile.getProfileData()
        return (
            str(self.username),
            str(self.email),
            full_name,
            bio,
            str(self.date_joined),
            avatar,
        )
