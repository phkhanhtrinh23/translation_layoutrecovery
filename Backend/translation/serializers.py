from rest_framework import serializers
from translation.models import PDF, Translation, Feedback


class PDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PDF
        fields = "__all__"


class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = "__all__"


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
