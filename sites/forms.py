from django.forms import ModelForm
from sites import models

class AuctionForm(ModelForm):
    class Meta:
        model = models.Auction
        fields = [
            'sending_site', 'start', 
            'end', 'starting_price_sqft', 
            'reserve_price_sqft'
            ]

    def __init__(self, user, *args, **kwargs):
        super(AuctionForm, self).__init__(*args, **kwargs)
        self.fields['sending_site'].queryset = models.SendingSite.objects.filter(user=user)