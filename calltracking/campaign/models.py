from django.db import models
from model_utils.models import TimeStampedModel
from campaign.managers import ActiveCampaignManager


class Campaign(TimeStampedModel):
    """ Campaigns are identified via the inbound number
    called by the user. In this example each campaign
    can only have a single inbound number
    """
    name = models.CharField(max_length=30)
    inbound_number = models.CharField(max_length=30)
    redirect_number = models.CharField(max_length=30)
    welcome_message = models.FileField(upload_to='audio/')
    is_active = models.BooleanField(default=False)

    active = ActiveCampaignManager()

