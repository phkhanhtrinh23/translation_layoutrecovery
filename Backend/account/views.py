import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.models import User, Profile, hash_password
from account.serializers import UserSerializer, ProfileSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.contrib.sessions.models import Session
from firebase_admin import credentials, initialize_app, storage
import firebase_admin
from dotenv import load_dotenv
from django.conf import settings

# Load the environment variables from the .env file
load_dotenv()

credential_json = settings.CREDENTIAL_JSON
storage_bucket = settings.STORAGE_BUCKET
avatar_folder = os.path.join(settings.MEDIA_ROOT, "Avatars")
pdf_folder = os.path.join(settings.MEDIA_ROOT, "PDFs")

# Init firebase with your credentials
if not firebase_admin._apps:
    cred = credentials.Certificate(credential_json)
    initialize_app(cred, {'storageBucket': storage_bucket})

class Register(APIView):
    def post(self, request, *args, **kwargs):
        user_data = JSONParser().parse(request)
        profile_serializers = ProfileSerializer(
            data={"full_name": user_data["full_name"], "bio": ""}
        )
        if profile_serializers.is_valid():
            profile_serializers.save()
        else:
            return Response(
                {"status": "error", "data": profile_serializers.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = Profile.objects.last()

        user_data.update({"profile": getattr(profile, "profile_id")})
        # Hashing the password
        user_data.update({"password": hash_password(user_data["password"])})
        user_serializers = UserSerializer(data=user_data)

        if user_serializers.is_valid():
            if user_serializers.is_valid():
                user_serializers.save()
                return Response(
                    {
                        "status": "success",
                        "data": {
                            key: value
                            for key, value in user_serializers.data.items()
                            if key != "password"
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "data": user_serializers.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            # modify error message when user is invalid --> trim the 'profile' message
            print(type(user_serializers.errors))
            error_response = {}
            error_response.update(user_serializers.errors)
            if "profile" in error_response:
                del error_response["profile"]
            return Response(
                {"status": "error", "data": error_response},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Login(APIView):
    def post(self, request, *args, **kwargs):
        try:
            user_data = JSONParser().parse(request)
            user_serializers = UserSerializer(data=user_data)

            temp_serializers = {}
            temp_serializers.update(user_serializers.initial_data)
            del temp_serializers["password"]

            for user in User.objects.all():
                if user.isAuthenticated(user_data["username"], user_data["password"]):
                    temp_serializers["profile"] = str(user.getProfileId())
                    temp_serializers["user_id"] = user.user_id
                    temp_serializers["email"] = user.email
                    return Response(
                        {"status": "Logged in successfully", "data": temp_serializers},
                        status=status.HTTP_200_OK,
                    )

            return Response(
                {
                    "status": "Wrong password or account doesn't exist!",
                    "data": temp_serializers,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:
            print(error)
            return Response(
                {"status": "Failed to log in", "data": user_data},
                status=status.HTTP_400_BAD_REQUEST,
            )


class Logout(APIView):
    def post(self, request, *args, **kwargs):
        response_data = {}
        try:
            sessionid = request.data.get("sessionid")
            userid = request.data.get("userid")
            print(sessionid, userid)
            # logout user by delete session id
            Session.objects.filter(session_key=sessionid).delete()
            response_data["status"] = "Logged out successfully"
        except Exception as error:
            print(error)
            return Response(
                {"status": "Failed to log out", "data": error},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(response_data, status=status.HTTP_200_OK)


class GetProfileData(APIView):
    def post(self, request, *args, **kwargs):
        profile_data = JSONParser().parse(request)
        profile_id = profile_data["profile_id"]
        try:
            full_name, bio, avatar = Profile.objects.filter(profile_id=profile_id).getProfileData()
            response_data = {}
            response_data["full_name"] = full_name
            response_data["bio"] = bio
            response_data["avatar"] = avatar
            return Response(
                {"status": "Got profile data successfully!", "data": response_data},
                status=status.HTTP_200_OK,
            )
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "data": "This profile does not exist!"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetUserData(APIView):
    def post(self, request, *args, **kwargs):
        # user_data = JSONParser().parse(request)
        username = kwargs.get("username")
        user_id = User.objects.get(username=username).user_id
        try:
            username, email, full_name, bio, date_joined, avatar = User.objects.get(
                user_id=user_id
            ).getUserData()
            response_data = {}
            response_data["username"] = username
            response_data["email"] = email
            response_data["full_name"] = full_name
            response_data["bio"] = bio
            response_data["date_joined"] = date_joined
            response_data["avatar"] = avatar
            return Response(
                {"status": "Got user data successfully!", "data": response_data},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"status": "error", "data": "This user does not exist!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

def save_uploaded_file(uploaded_file , destination_path):
    # Step 0: Check if the destination path exists, if not, create it
    os.makedirs(destination_path, exist_ok=True)

    # Step 1: Access the file content
    file_content = uploaded_file.read()
    
    # Step 2: Choose a destination path (including filename)
    full_destination_path = os.path.join(destination_path, uploaded_file.name)
    
    # Step 3: Write content to the file
    with open(full_destination_path, 'wb') as destination_file:
        destination_file.write(file_content)

class UpdateProfile(APIView):
    def post(self, request, *args, **kwargs):
        username = kwargs.get("username")
        profile_data = request.data
        user_id = User.objects.get(username=username).user_id
        full_name = profile_data["full_name"]
        bio = profile_data["bio"]
        avatar = profile_data["avatar"]
        try:
            profile = User.objects.get(user_id=user_id).profile
            img_name = str(avatar)

            # save the avatar file to avatar folder
            save_uploaded_file(avatar, avatar_folder)

            # Put your local file path 
            fileName = os.path.join(avatar_folder, img_name)
            bucket = storage.bucket()
            blob = bucket.blob(img_name)
            blob.upload_from_filename(fileName)

            # make public access from the URL
            blob.make_public()

            # delete avatar just saved from avatar folder
            os.remove(fileName)

            profile.updateName(full_name)
            profile.updateBio(bio)
            profile.updateAvatar(blob.public_url)

            response_data = {}
            response_data["full_name"] = full_name
            response_data["bio"] = bio
            response_data["avatar"] = blob.public_url
            print(response_data["avatar"])
            

            return Response(
                {"status": "Updated profile data successfully!", "data": response_data},
                status=status.HTTP_200_OK,
            )
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "data": "This profile does not exist!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
