from django.views.generic import TemplateView
from app.forms import FormForm
from django.shortcuts import render


# class MyView(TemplateView):
def country_form(request):
    # instead of hardcoding a list you could make a query of a model, as long as
    # it has a __str__() method you should be able to display it.
    country_list = ("Mexico", "USA", "China", "France")
    form = FormForm(data_list=country_list)

    return render(request, "index.html", {"form": form})
