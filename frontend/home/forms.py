from django import forms
from .fields import ListTextWidget


class SearchForm(forms.Form):
    base_point = forms.CharField(
        label="出発地点:",
        required=True,
        max_length=255,
        widget=forms.Textarea(attrs={"cols": "400", "rows": "20"}),
    )

    def __init__(self, *args, **kwargs):
        point_list = kwargs.pop("data_list", None)
        super(SearchForm, self).__init__(*args, **kwargs)

        # the "name" parameter will allow you to use the same widget more than once in the same
        # form, not setting this parameter differently will cuse all inputs display the
        # same list.
        self.fields["base_point"].widget = ListTextWidget(
            data_list=point_list, name="point_list"
        )
