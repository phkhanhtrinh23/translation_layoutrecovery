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
from PIL import Image
import base64

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

def save_uploaded_file(uploaded_file , destination_path, file_name):
    """
    Save an uploaded file to a specified destination path.

    Args:
        uploaded_file (File): The uploaded file object.
        destination_path (str): The path where the file will be saved.

    Returns:
        None
    """
    # Step 0: Check if the destination path exists, if not, create it
    os.makedirs(destination_path, exist_ok=True)

    # Step 1: Choose a destination path (including filename)
    full_destination_path = os.path.join(destination_path, file_name)

    # Step 3: Decode the string base64 to an image
    # Remove the 'data:image/jpeg;base64,' prefix and decode the image data
    _, context = context.split(",", 1)
    image_64_decode = base64.b64decode(context)

    # Step 4: create a writable image and write the decoding result
    image_result = open(full_destination_path, "wb")
    image_result.write(image_64_decode)

class Register(APIView):
    def post(self, request, *args, **kwargs):
        """
        This function handles the HTTP POST request. It receives the request object, which contains the data sent by the client. The function expects a JSON object in the request body, containing the user's full name and password. It returns a response object with the appropriate status code and data.

        Parameters:
            request: The HTTP request object containing the JSON data sent by the client.

        Returns:
            response: The HTTP response object containing the result of the POST request. If the request is valid, a success response is returned with the user data excluding the password. If the request is invalid, an error response is returned with the appropriate status code and error message.
        """
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
        """
        Handles the POST request for logging in a user.

        Args:
            request: The request object containing the user data.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the login status and user data.
        """
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
        """
        Handles the POST request to log out a user.
        
        Parameters:
            request (Request): The HTTP request object.
            args (list): Positional arguments passed to the function.
            kwargs (dict): Keyword arguments passed to the function.
        
        Returns:
            Response: The HTTP response object containing the result of the logout operation.
        """
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
        """
        Handles the HTTP POST request to retrieve profile data.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response containing the profile data.
        """
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
        """
        This function handles the HTTP POST request to retrieve user data.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args (tuple): Variable length argument list.
            **kwargs (dict): Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object containing the retrieved user data or an error message.
        """
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

class UpdateProfile(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to update a user's profile data.

        Parameters:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object containing the updated profile data.
        """
        username = kwargs.get("username")
        profile_data = request.data
        user_id = User.objects.get(username=username).user_id
        full_name = profile_data["full_name"]
        bio = profile_data["bio"]
        avatar = profile_data["avatar"]
        print(avatar)
        try:
            profile = User.objects.get(user_id=user_id).profile
            img_name = str(avatar)

            # save the avatar file to avatar folder
            save_uploaded_file(avatar, avatar_folder, username)

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
