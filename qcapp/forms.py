from django import forms

class CampaignForm(forms.Form):

   title = forms.CharField(label='Set Campaign Name', max_length=100,widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))
   deadline = forms.DateField(label = 'Set Campaign Deadline',widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))
   description = forms.CharField(label = 'Set Campaign Details (Optional)', required = False, widget = forms.Textarea(attrs={'class' : 'form-control clean-look'}))
   contact = forms.CharField(label = 'Set Campaign Contact Information (Optional)', max_length=100, required = False,widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))
