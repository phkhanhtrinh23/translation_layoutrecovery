from rest_framework import serializers
from translation.models import PDF, Translation, Feedback


class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = ("pdf_id", "owner_id", "file_name", "file", "language")


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = ("translation_id", "file_input")


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ("feedback_id", "user_id", "pdf_id", "rating")
