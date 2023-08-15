from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.


def generate_username(email):
    return email.split("@")[0]


# def generate_profile_id():
#     try:
#         last_id_record = Profile.objects.last()
#         if last_id_record:
#             last_id = last_id_record.profile_id
#         else:
#             last_id = 0

#         new_id = last_id + 1
#         return new_id
#     except Exception as e:
#         # Handle any exceptions that might occur during ID generation
#         print(f"An error occurred: {e}")
#         return None


def isAbleToUpdatePassword(self, new_password):
    return (
        new_password != self.password
        and new_password != ""
        and len(new_password) >= 6
        and len(new_password) <= 64
    )


def hash_password(password):
    return make_password(password)


class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True, unique=True)
    full_name = models.CharField(max_length=255, blank=False)
    bio = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to="Avatar/", default="Avatar/avatar.png")

    def __str__(self):
        return str(self.profile_id)

    def save(self, *args, **kwargs):
        if not self.profile_id:
            last_profile = Profile.objects.last()
            last_id = last_profile.profile_id if last_profile else 0
            self.profile_id = last_id + 1
        super().save(*args, **kwargs)

    def getFullName(self):
        return str(self.full_name)

    def updateName(self, full_name):
        if full_name != "":
            self.full_name = full_name
            super(Profile, self).save()
            return True
        else:
            return False

    def updateBio(self, bio):
        if bio != "":
            self.bio = bio
            super(Profile, self).save()
            return True
        else:
            return False

    def updateAvatar(self, avatar):
        if avatar != None:
            self.avatar = avatar
            super(Profile, self).save()
            return True
        else:
            return False

    def getProfileData(self):
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
        if not self.user_id:
            last_user = User.objects.last()
            last_id = last_user.user_id if last_user else 0
            self.user_id = last_id + 1
        super().save(*args, **kwargs)

    def isAuthenticated(self, username, password):
        return username == self.username and check_password(password, self.password)

    def getProfileId(self):
        return str(self.profile_id)

    def updatePassword(self, new_password):
        if isAbleToUpdatePassword(self, new_password):
            self.password = new_password
            return True
        return False

    def getUserData(self):
        full_name, bio, avatar = self.profile.getProfileData()
        return (
            str(self.username),
            str(self.email),
            full_name,
            bio,
            str(self.date_joined),
            avatar,
        )
