import os
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from account.models import User, Profile
from translation.models import PDF, Translation, Feedback
from translation.serializers import (
    PDFSerializer,
    TranslationSerializer,
    FeedbackSerializer,
)

import shutil


# from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from firebase_admin import credentials, initialize_app, storage
import firebase_admin
from dotenv import load_dotenv
from django.conf import settings

from Model.main import TranslationLayoutRecovery

# Load the environment variables from the .env file
load_dotenv()

credential_json = settings.CREDENTIAL_JSON
storage_bucket = settings.STORAGE_BUCKET
avatar_folder = os.path.join(settings.MEDIA_ROOT, "Avatars")
pdf_folder = os.path.join(settings.MEDIA_ROOT, "PDFs")

obj = TranslationLayoutRecovery()

# Init firebase with your credentials
if not firebase_admin._apps:
    cred = credentials.Certificate(credential_json)
    initialize_app(cred, {"storageBucket": storage_bucket})


# Create your views here.
def getAllPDFs():
    """
    Retrieves all the PDF objects from the database and returns them as a list.
    
    Returns:
        list: A list of PDF objects.
    """
    pdfs = list(PDF.objects.all().values())
    return pdfs


def getUserPDFs(user_id, search=None):
    """
    Retrieves a list of PDFs owned by a given user.

    Args:
        user_id (int): The ID of the user.
        search (str, optional): The search string to filter PDFs by file name. Defaults to None.

    Returns:
        list: A list of dictionaries representing the PDFs. Each dictionary contains details such as file name, owner ID, etc.
    """
    pdfs = (
        list(PDF.objects.filter(file_name__contains=search, owner_id=user_id).values())
        if search
        else list(PDF.objects.filter(owner_id=user_id).values())
    )
    return pdfs


def getUserTranslations(user_id):
    """
    Get the translations associated with a specific user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of translations associated with the user.
    """
    translations = list(
        Translation.objects.filter(file_input__owner_id=user_id).values()
    )
    return translations


def updateOutput(translation_id, user_id, new_pdf_id):
    """
    Updates the output of a translation with a new PDF file.

    Args:
        translation_id (int): The ID of the translation.
        user_id (int): The ID of the user.
        new_pdf_id (int): The ID of the new PDF file.

    Returns:
        bool: True if the output is successfully updated, False otherwise.
    """
    translation = Translation.objects.get(translation_id=translation_id)
    user = User.objects.get(user_id=user_id)
    new_pdf = PDF.objects.get(pdf_id=new_pdf_id)
    if translation and user and new_pdf:
        check_update = translation.isAbleToUpdate()
        if check_update:
            try:
                translation.updateFileOutput(new_pdf)
                translation.updateStatus(1)
                return True
            except:
                translation.updateStatus(-1)

        return False
    return False


def save_uploaded_file(uploaded_file, pdf_name, destination_path):
    """
    Saves an uploaded file to a specified destination path.

    Parameters:
        uploaded_file (file-like object): The uploaded file to be saved.
        destination_path (str): The path where the file should be saved.

    Returns:
        None
    """
    # Step 0: Check if the destination path exists, if not, create it
    os.makedirs(destination_path, exist_ok=True)

    # Step 1: Access the file content
    print(uploaded_file)
    file_content = uploaded_file.read()

    # Step 2: Choose a destination path (including filename)
    full_destination_path = os.path.join(destination_path, pdf_name)

    # Step 3: Write content to the file
    with open(full_destination_path, "wb") as destination_file:
        destination_file.write(file_content)


class GetUserPDFs(APIView):
    def get(self, request, *args, **kwargs):
        """
        Retrieves user-specific PDFs based on the provided username and query parameters.

        Args:
            request (Request): The request object.
            args (Any): Variable length argument list.
            kwargs (Any): Arbitrary keyword arguments.

        Returns:
            Response: The response object containing the status and data.
        """
        try:
            username = kwargs.get("username")
            user_id = (
                User.objects.filter(username=username)
                .values("user_id")
                .first()["user_id"]
            )
            op = request.query_params.get("type")
            if op == "all":
                ans = getUserPDFs(user_id)
            elif op == "search":
                search = request.query_params.get("query")
                if search == None:
                    search = ""
                ans = getUserPDFs(user_id, search)
            else:
                ans = "Nothing"
            return Response(
                {"status": "success", "data": ans}, status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreatePDF(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles a POST request to upload a PDF file.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object.

        Raises:
            Exception: If there is an error processing the request.
        """
        try:
            pdf_data = request.data
            user_id = pdf_data["user_id"]
            file = pdf_data["file"]
            language = pdf_data["language"]

            # get file name
            pdf_name = str(file).split(".")[0] + "_" + str(time.time()).split(".")[0] + ".pdf"
            # save file to pdf folder
            save_uploaded_file(file, pdf_name, pdf_folder)
            # upload file just saved to firebase storage
            fileName = os.path.join(pdf_folder, pdf_name)
            bucket = storage.bucket()
            blob = bucket.blob(pdf_name)
            blob.upload_from_filename(fileName)

            # make public access from the URL
            blob.make_public()

            # delete avatar just saved from avatar folder
            # os.remove(fileName)

            if User.objects.filter(user_id=user_id).exists():
                current_data = {}
                current_data["owner_id"] = user_id
                current_data["file_name"] = str(file)
                current_data["file"] = blob.public_url
                current_data["language"] = language
                print(len(str(current_data["file"])))

                pdf_serializer = PDFSerializer(data=current_data)
                if pdf_serializer.is_valid():
                    pdf_serializer.save()
                    return Response(
                        {"status": "success", "data": pdf_serializer.data},
                        status=status.HTTP_200_OK,
                    )
                print(pdf_serializer.errors)
                return Response(
                    {"status": "error", "data": pdf_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProcessTranslation(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles a POST request to translate a pdf file.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object.

        Raises:
            Exception: If there is an error processing the request.
        """
        translation_data = request.data
        try:
            if PDF.objects.filter(pdf_id=translation_data["file_input"]).exists():
                file_input = PDF.objects.get(pdf_id=translation_data["file_input"])

                # get the random number of file
                random_number = str(file_input.file).split("/")[-1].split("_")[-1].split(".")[0]
                # get file name
                input_name = str(file_input.file_name).split(".")[0] + "_" + random_number + ".pdf"
                
                output_name = (
                    str(file_input.file_name).split(".")[0] + "_translated_" + str(translation_data["language"]) + ".pdf"
                )

                random_output_name = str(file_input.file_name).split(".")[0] + "_" + random_number + "_translated_" + str(translation_data["language"]) + ".pdf"

                # get language
                original_language = file_input.language
                target_language = translation_data["language"]

                # main process...
                # upload file just saved to firebase storage
                file_name_input = os.path.join(pdf_folder, input_name)
                file_name_output = os.path.join(pdf_folder, random_output_name)
                
                
                # TODO: process file_output by using AI model and update later...
                obj.translate_pdf(
                    language=target_language,
                    input_path=file_name_input,
                    output_path=pdf_folder,
                    merge=False,
                )
                temp_file = os.path.join(pdf_folder, "fitz_translated.pdf")

                shutil.copyfile(temp_file, file_name_output)
                os.remove(temp_file)
                
                bucket = storage.bucket()
                blob = bucket.blob(random_output_name)
                blob.upload_from_filename(file_name_output)

                # make public access from the URL
                blob.make_public()

                # delete original pdf and output pdf just saved from pdf folder
                os.remove(file_name_input)
                os.remove(file_name_output)

                new_pdf = PDF(
                    owner_id=file_input.owner_id,
                    file=blob.public_url,
                    language=target_language,
                    file_name=output_name,
                )
                new_pdf.save()

                current_data = {}
                current_data["status"] = 1
                current_data["file_input"] = file_input.pdf_id
                current_data["file_output"] = new_pdf.pdf_id
                translation_serializer = TranslationSerializer(data=current_data)
                if translation_serializer.is_valid():
                    translation_serializer.save()
                    current_data = translation_serializer.data
                    current_data.update({"file_input_url": file_input.getFileUrl(), "file_output_url": new_pdf.getFileUrl()})
                    return Response(
                        {"status": "success", "data": current_data},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"status": "error", "data": translation_serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                current_data = {}
                current_data["status"] = -1
                current_data["file_input"] = translation_data["file_input"]
                current_data["file_output"] = "Null"
                translation_serializer = TranslationSerializer(data=current_data)
                if translation_serializer.is_valid():
                    translation_serializer.save()
                    return Response(
                        {"status": "failure", "data": translation_serializer.data},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"status": "error", "data": "Invalid request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print(e)
            return Response(
                {"status": "failure", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetTranslationData(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles a POST request to get the translation data.

        Parameters:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The HTTP response object.

        Raises:
            Exception: If there is an error processing the request.
        """
        input_data = JSONParser().parse(request)
        translation_id = input_data["translation_id"]
        try:
            (
                file_input,
                file_output,
                username,
                status,
            ) = Translation.objects.get(
                translation_id=translation_id
            ).getTranslationData()
            response_data = {}
            response_data["file_input"] = file_input
            response_data["file_output"] = file_output
            response_data["username"] = username
            response_data["status"] = status
            return Response(
                {"status": "Got translation data successfully!", "data": response_data},
                status=status.HTTP_200_OK,
            )
        except Translation.DoesNotExist:
            return Response(
                {"status": "error", "data": "This translation does not exist!"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FeedbackPDF(APIView):
    def post(self, request, *args, **kwargs):
        """
        Handles the HTTP POST request for creating a new feedback entry.

        Parameters:
            request (HttpRequest): The HTTP request object.
            args (tuple): Additional positional arguments.
            kwargs (dict): Additional keyword arguments.

        Returns:
            Response: The HTTP response object containing the status and data.

        Raises:
            Exception: If there is an error while processing the request.
        """
        try:
            data = JSONParser().parse(request)
            user_id = data["user_id"]
            translation_id = data["translation_id"]
            rating = data["rating"]
            if (
                User.objects.filter(user_id=user_id).exists()
                and Translation.objects.filter(translation_id=translation_id).exists()
            ):
                feedback_serializer = FeedbackSerializer(data=data)
                if feedback_serializer.is_valid():
                    feedback_serializer.save()
                return Response(
                    {"status": "success", "data": "Feedback successfully!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "data": "Invalid user or translation"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        """
        Deletes a feedback entry.

        Parameters:
            request (Request): The HTTP request object.
            args (list): Additional positional arguments.
            kwargs (dict): Additional keyword arguments.

        Returns:
            Response: The HTTP response object.
        """
        try:
            data = JSONParser().parse(request)
            user_id = data["user_id"]
            translation_id = data["translation_id"]
            if (
                User.objects.filter(user_id=user_id).exists()
                and PDF.objects.filter(token_id=translation_id).exists()
            ):
                feedback = Feedback.objects.get(
                    user_id=user_id, translation_id=translation_id
                )
                feedback.delete()
                return Response(
                    {"status": "success", "data": "Remove feedback successfully!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "data": "Invalid user or translation"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get(self, request, *args, **kwargs):
        """
        Retrieves a list of PDF objects based on the provided user ID.

        Parameters:
            request (HttpRequest): The HTTP request object.
            args (tuple): Any additional positional arguments.
            kwargs (dict): Any additional keyword arguments. Should contain the "user_id" key.

        Returns:
            Response: The response object containing the list of PDF objects, or an error message if the request is invalid.
        """
        try:
            user_id = kwargs.get("user_id")
            if User.objects.filter(user_id=user_id).exists():
                feedbacks = Feedback.objects.filter(user_id=user_id).values(
                    "translation_id"
                )
                translation_ids = [feedback["translation_id"] for feedback in feedbacks]
                res = list(
                    PDF.objects.filter(translation_id__in=translation_ids).values()
                )
                return Response(
                    {"status": "success", "data": res}, status=status.HTTP_200_OK
                )
        except:
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class HistoryView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Retrieves data for a specific user.

        Parameters:
            request (Request): The HTTP request object.
            args (tuple): Positional arguments.
            kwargs (dict): Keyword arguments.

        Returns:
            Response: The HTTP response object containing the retrieved data.

        Raises:
            HTTP_400_BAD_REQUEST: If the request is invalid or the user is not found.
        """
        try:
            username = kwargs.get("username")
            if User.objects.filter(username=username).exists():
                user_id = User.objects.get(username=username).user_id
                data = []
                translations = list(
                    Translation.objects.filter(file_input__owner_id=user_id).values()
                )
                print(type(translations[0]))
                for translation in translations:
                    print(translation)
                    temp_translation = Translation.objects.get(translation_id=translation["translation_id"])
                    translation_info = {
                        "file_input": temp_translation.getFileInputName(),
                        "file_input_url": temp_translation.getFileInput().getFileUrl(),
                        "file_output": temp_translation.getFileOutputName(),
                        "file_output_url": temp_translation.getFileOutput().getFileUrl(),
                        "status": temp_translation.getStatus(),
                        "time": temp_translation.time_stamp,
                    }
                    print(translation_info)
                    data.append(translation_info)
                return Response(
                    {"status": "success", "data": data}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"status": "User not found!", "data": "Invalid user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )
