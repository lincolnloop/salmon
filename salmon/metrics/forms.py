from django import forms


class FilterHistory(forms.Form):
    from_date = forms.DateTimeField(required=False)
    to_date = forms.DateTimeField(required=False)
