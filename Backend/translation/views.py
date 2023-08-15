from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from account.models import User, Profile
from translation.models import PDF, Translation, Feedback
from translation.serializers import (
    PDFSerializer,
    TranslationSerializer,
    FeedbackSerializer,
)
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser


# Create your views here.
def getAllPDFs():
    pdfs = list(PDF.objects.all().values())
    return pdfs


def getUserPDFs(user_id, search=None):
    pdfs = list(PDF.objects.filter(title__contains=search, owner_id=user_id).values())
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


class GetUserPDFs(APIView):
    def get(self, request, *args, **kwargs):
        try:
            username = kwargs.get("username")
            user_id = (
                User.objects.filter(username=username)
                .values("user_id")
                .first()["user_id"]
            )
            ans = getUserPDFs(user_id)
            return Response(
                {"status": "success", "data": ans}, status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GetUserTranslations(APIView):
    def get(self, request, *args, **kwargs):
        try:
            username = kwargs.get("username")
            user_id = (
                User.objects.filter(username=username)
                .values("user_id")
                .first()["user_id"]
            )
            ans = getUserTranslations(user_id)
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
        try:
            current_data = {
                "owner_id": request.data["user_id"],
                "file_name": request.data["file_name"],
                "file": request.data["file"],
                "language": request.data["language"],
            }

            print(current_data)

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
        translation_data = JSONParser().parse(request)
        translation_serializers = TranslationSerializer(data=translation_data)
        if translation_serializers.is_valid():
            translation_serializers.save()
            print(translation_serializers.data)
            translation_id = translation_serializers.data["translation_id"]
            file_input_id = translation_serializers.data["file_input"]

            # TODO:
            # process file_output_id by using AI model and update later...
            file_output_id = 1

            user_id = PDF.objects.get(pdf_id=file_input_id).owner_id.user_id
            if updateOutput(translation_id, user_id, file_output_id):
                return Response(
                    {"status": "success", "data": "Translation success!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"status": "error", "data": "Translation failed!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"status": "error", "data": translation_serializers.errors},
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
                feedback = Feedback.objects.get(user_id=user_id, translation_id=translation_id)
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
                feedbacks = Feedback.objects.filter(user_id=user_id).values("translation_id")
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
                translations = list(Translation.objects.filter(file_input__owner_id=user_id).values())
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
                    {"status": "error", "data": "Invalid pdf"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except:
            return Response(
                {"status": "error", "data": "Invalid request"},
                status=status.HTTP_400_BAD_REQUEST,
            )
