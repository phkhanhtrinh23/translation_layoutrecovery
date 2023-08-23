from django.urls import path, include, re_path
from .views import (
    GetUserPDFs,
    ProcessTranslation,
    CreatePDF,
    # GetUserTranslations,
    GetTranslationData,
    FeedbackPDF,
    HistoryView,
)


urlpatterns = [
    path("create", CreatePDF.as_view(http_method_names=['post'])), # create pdf OK
    path("translation", ProcessTranslation.as_view()), # translate pdf ...
    path('pdf/<str:username>', GetUserPDFs.as_view()), # get pdfs by username OK
    path('gettranslation', GetTranslationData.as_view()), # get translation data by translation_id
    path('history/<str:username>', HistoryView.as_view()),  # get translation history by username
    # path('translations/<str:username>', GetUserTranslations.as_view()), # get translations by username
    
    path('feedback', FeedbackPDF.as_view(http_method_names=['post'])), # post feedback
    path('feedback/<int:user_id>', FeedbackPDF.as_view(http_method_names=['get'])), # get feedback by user_id
    path('removefeedback', FeedbackPDF.as_view(http_method_names=['delete'])), # delete feedback
]
