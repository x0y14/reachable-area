from django import forms
from app.fields import ListTextWidget


class FormForm(forms.Form):
    from_ = forms.CharField(
        label="出発地点:",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        _country_list = kwargs.pop("data_list", None)
        super(FormForm, self).__init__(*args, **kwargs)

        # the "name" parameter will allow you to use the same widget more than once in the same
        # form, not setting this parameter differently will cuse all inputs display the
        # same list.
        self.fields["from_"].widget = ListTextWidget(
            data_list=_country_list, name="country-list"
        )
