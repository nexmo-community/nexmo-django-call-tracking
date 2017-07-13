from django.conf.urls import url
from campaign.views import AnswerView, RecordView, EventsView


urlpatterns = [
    url(r'^answer/', AnswerView.as_view()),
    url(r'^record/', RecordView.as_view()),
    url(r'^events/', EventsView.as_view())
]
