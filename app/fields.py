from django import forms

from engine.transit_type import TransitType


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
            if int(data[0]) == int(TransitType.TRAIN):
                label = f"🚃{data[2]}/{data[3]}"
                value = data[3]
            elif int(data[0]) == int(TransitType.BUS):
                label = f"🚌{data[1]}/{data[2]}"
                value = data[2]
            data_list += f"<option label='{label}' value='{value}'>"
        data_list += "</datalist>"

        return text_html + data_list
