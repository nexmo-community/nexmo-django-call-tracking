from django.db import models
from django.db.models import Q


class ActiveCampaignManager(models.Manager):
    def get_queryset(self):
        return super(ActiveCampaignManager, self).get_queryset().filter(is_active=True)

    def for_number(self, to_number):
        campaigns = self.get_queryset().filter(Q(inbound_number=to_number) | Q(redirect_number=to_number))
        
        return campaigns[0] if campaigns.exists() else None
