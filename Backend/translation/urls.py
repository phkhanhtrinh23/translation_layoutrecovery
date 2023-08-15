from django.urls import path, include, re_path
from account import api_handler
from .views import (
    GetUserPDFs,
    ProcessTranslation,
    CreatePDF,
    GetUserTranslations,
    GetTranslationData,
    FeedbackPDF,
    HistoryView,
)


urlpatterns = [
    path("translation", ProcessTranslation.as_view()),
    path("create", CreatePDF.as_view()),
    path('pdf/<str:username>', GetUserPDFs.as_view()),
    path('translations/<str:username>', GetUserTranslations.as_view()),
    path('gettranslation', GetTranslationData.as_view()),
    path('feedback', FeedbackPDF.as_view(http_method_names=['post'])),
    path('feedback/<int:user_id>', FeedbackPDF.as_view(http_method_names=['get'])),
    path('removefeedback', FeedbackPDF.as_view(http_method_names=['delete'])),
    path('history/<str:username>', HistoryView.as_view()),
]
