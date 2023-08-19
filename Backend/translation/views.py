import os
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

# from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
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
    initialize_app(cred, {"storageBucket": storage_bucket})


# Create your views here.
def getAllPDFs():
    pdfs = list(PDF.objects.all().values())
    return pdfs


def getUserPDFs(user_id, search=None):
    pdfs = (
        list(PDF.objects.filter(file_name__contains=search, owner_id=user_id).values())
        if search
        else list(PDF.objects.filter(owner_id=user_id).values())
    )
    return pdfs


def getUserTranslations(user_id):
    translations = list(
        Translation.objects.filter(file_input__owner_id=user_id).values()
    )
    return translations


def updateOutput(translation_id, user_id, new_pdf_id):
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


def save_uploaded_file(uploaded_file, destination_path):
    # Step 0: Check if the destination path exists, if not, create it
    os.makedirs(destination_path, exist_ok=True)

    # Step 1: Access the file content
    file_content = uploaded_file.read()

    # Step 2: Choose a destination path (including filename)
    full_destination_path = os.path.join(destination_path, uploaded_file.name)

    # Step 3: Write content to the file
    with open(full_destination_path, "wb") as destination_file:
        destination_file.write(file_content)


class GetUserPDFs(APIView):
    def get(self, request, *args, **kwargs):
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


# class GetUserTranslations(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             username = kwargs.get("username")
#             user_id = (
#                 User.objects.filter(username=username)
#                 .values("user_id")
#                 .first()["user_id"]
#             )
#             ans = getUserTranslations(user_id)
#             return Response(
#                 {"status": "success", "data": ans}, status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             print(e)
#             return Response(
#                 {"status": "error", "data": "Invalid request"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


class CreatePDF(APIView):
    def post(self, request, *args, **kwargs):
        try:
            pdf_data = request.data
            user_id = pdf_data["user_id"]
            file = pdf_data["file"]
            language = pdf_data["language"]

            # get file name
            pdf_name = str(file)
            # save file to pdf folder
            save_uploaded_file(file, pdf_folder)
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
        translation_data = request.data
        try:
            if PDF.objects.filter(pdf_id=translation_data["file_input"]).exists():
                file_input = PDF.objects.get(pdf_id=translation_data["file_input"])

                # TODO: process file_output by using AI model and update later...

                # get file name
                input_name = str(file_input.file_name)
                output_name = (
                    str(file_input.file_name).split(".")[0] + "_translated.pdf"
                )

                # get language
                original_language = file_input.language
                target_language = translation_data["language"]

                # main process...

                # save file to pdf folder
                # save_translated_file(output_pdf_name, pdf_folder)

                # upload file just saved to firebase storage
                file_name_output = os.path.join(pdf_folder, output_name)
                bucket = storage.bucket()
                blob = bucket.blob(output_name)
                blob.upload_from_filename(file_name_output)

                # make public access from the URL
                blob.make_public()

                # delete original pdf and output pdf just saved from pdf folder
                os.remove(os.path.join(pdf_folder, input_name))
                os.remove(file_name_output)

                new_pdf = PDF(
                    owner_id=file_input.owner_id,
                    file=blob.public_url,
                    language=target_language,
                )
                new_pdf.save()

                current_data = {}
                current_data["status"] = 1
                current_data["file_input"] = file_input.pdf_id
                current_data["file_output"] = new_pdf.pdf_id
                translation_serializer = TranslationSerializer(data=current_data)
                if translation_serializer.is_valid():
                    translation_serializer.save()
                    return Response(
                        {"status": "success", "data": translation_serializer.data},
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
        try:
            username = kwargs.get("username")
            if User.objects.filter(username=username).exists():
                user_id = User.objects.get(username=username).user_id
                data = []
                translations = list(
                    Translation.objects.filter(file_input__owner_id=user_id).values()
                )
                for translation in translations:
                    translation_info = {
                        "file_input": translation.getFileInputName(),
                        "file_output": translation.getFileOutputName(),
                        "status": translation.getStatus(),
                        "time": translation.time_stamp,
                    }
                    data.append(translation_info)
                return Response(
                    {"status": "success", "data": data}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"status": "error", "data": "Invalid user"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )
