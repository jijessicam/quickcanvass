from django import forms

class CampaignForm(forms.Form):

   title = forms.CharField(label='Set Campaign Name', max_length=100,widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))
   deadline = forms.DateField(label = 'Set Campaign Deadline',widget=forms.SelectDateWidget(attrs={'class' : 'testing'}))
   targetted_years = forms.ChoiceField(label = 'Set Targeted Class Year', choices=[("any", "All Years"), ("2020", "2020"), ("2019", "2019"), ("2018", "2018"), ("2017", "2017")], widget=forms.Select(attrs={'class':'form-control clean-look selector'}))
   description = forms.CharField(label = 'Set Campaign Details (Optional)', required = False, widget = forms.Textarea(attrs={'class' : 'form-control clean-look'}))
   contact = forms.CharField(label = 'Set Campaign Contact Information (Optional)', max_length=100, required = False,widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))

class SurveyForm(forms.Form):
	script = forms.CharField(label='Script for Canvassers', max_length=600, widget=forms.Textarea(attrs={'class' : 'form-control clean-look'}))
	q1 = forms.CharField(label='Question 1', max_length=200, required = False, widget=forms.Textarea(attrs={'class' : 'form-control clean-look'}))
	q2 = forms.CharField(label='Question 2', max_length=200, required = False, widget=forms.Textarea(attrs={'class' : 'form-control clean-look'}))
	q3 = forms.CharField(label='Question 3', max_length=200, required = False, widget=forms.Textarea(attrs={'class' : 'form-control clean-look'}))
class FillSurveyForm(forms.Form):
	script = forms.CharField(label='', max_length=500, widget=forms.Textarea(attrs={'class' : 'form-control clean-look'}))
	q1 = forms.CharField(label='', max_length=200,  required = False, widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))
	q2 = forms.CharField(label='', max_length=200,  required = False, widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))
	q3 = forms.CharField(label='', max_length=200,  required = False, widget=forms.TextInput(attrs={'class' : 'form-control clean-look'}))
