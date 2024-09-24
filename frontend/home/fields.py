from django import forms
from django.utils.safestring import mark_safe


class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({"list": "list__%s" % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for data in self._list:
            label = ""
            value = ""
            if int(data[0]) == int(1):
                label = f"🚃{data[2]}/{data[3]}"
                value = f"1/{data[2]}/{data[3]}"
                # value = label
            elif int(data[0]) == int(2):
                label = f"🚌{data[1]}/{data[2]}"
                value = f"2/{data[1]}/{data[2]}"
                # value = label
            data_list += f"<option label='{label}' value='{value}'>"
        data_list += "</datalist>"

        return text_html + mark_safe(data_list)
