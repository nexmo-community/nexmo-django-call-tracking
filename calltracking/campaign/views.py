import json
import nexmo
import requests

from django.views.generic import View, TemplateView
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from annoying.functions import get_object_or_None
from mixpanel import Mixpanel
from campaign.models import Campaign


class AnswerView(TemplateView):
    content_type = 'application/json'
    campaign_template = 'campaign/campaign.json'
    no_campaign_template = 'campaign/not-found.json'

    def get_context_data(self, **kwargs):
        inbound_number = self.request.GET.get('to', None)
        kwargs['from_number'] = self.request.GET.get('from', None)
        self.campaign = Campaign.active.for_number(inbound_number)
        kwargs['campaign'] = self.campaign

        return super(AnswerView, self).get_context_data(**kwargs)

    def get_template_names(self):
        return [self.campaign_template] if self.campaign else [self.no_campaign_template]

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


@method_decorator(csrf_exempt, name='dispatch')
class EventsView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        # We only want to record completed calls in this instance
        if data['status'] == 'completed':
            campaign = Campaign.active.for_number(data['to'])

            if campaign:
                mix = Mixpanel(settings.MIXPANEL_TOKEN)
                client = nexmo.Client(
                    key=settings.NEXMO_API_KEY,
                    secret=settings.NEXMO_API_SECRET
                )

                # Track people data
                insight = client.get_advanced_number_insight(number=data['from'])

                mix.people_set(
                    insight['international_format_number'],
                    {
                        '$phone': '+' + insight.get('international_format_number'),
                        '$first_name': insight.get('first_name'),
                        '$last_name': insight.get('last_name'),
                        'Country': insight.get('country_name'),
                        'Country Code': insight.get('country_code_iso3'),
                        'Valid Number': insight.get('valid_number'),
                        'Reachable': insight.get('reachable'),
                        'Ported': insight.get('ported'),
                        'Roaming': insight.get('roaming').get('status'),
                        'Carrier Name': insight.get('current_carrier').get('name'),
                        'Network Type': insight.get('current_carrier').get('network_type'),
                        'Network Country': insight.get('current_carrier').get('country'),
                    }
                )

                # Track call data
                mix.track(
                    insight['international_format_number'],
                    'inbound call',
                    {
                        'Campaign ID': campaign.pk,
                        'Campaign Name': campaign.name,
                        'Duration': data.get('duration'),
                        'Start Time': data.get('start_time'),
                        'End Time': data.get('end_time'),
                        'Price': data.get('price')
                    }
                )

        return HttpResponse()


@method_decorator(csrf_exempt, name='dispatch')
class RecordView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        recording = requests.get(data['recording_url'], params={
            'api_key': settings.NEXMO_API_KEY,
            'api_secret': settings.NEXMO_API_SECRET
        })

        return HttpResponse(recording.status_code)
