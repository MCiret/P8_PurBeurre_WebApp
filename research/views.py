import research.substitutes_research as subr
from django.shortcuts import render
from django.views.generic import TemplateView


class HomePageView(TemplateView):
    template_name = 'research/home.html'


class ResultView(TemplateView):
    template_name = 'research/result.html'

    def get(self, request, *args, **kwargs):
        # if it's user's research (keywords submitting) :
        if request.GET:
            context = subr.researchs_in_db(research_keywords=request.GET.get('research'))
        # when research returned several foods and user had selected 1
        elif self.kwargs:
            context = subr.researchs_in_db(food_barcode=self.kwargs['selected_food'])

        return render(request, self.template_name, context)
