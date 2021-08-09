from django.shortcuts import render
from django.views.generic import TemplateView, View, DetailView
import research.substitutes_research as subr
from research.models import Food
from research.forms import ResearchForm
import bookmark.bookmarks_db_handler as bdh


class HomePageView(TemplateView):
    template_name = 'research/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['research_form'] = ResearchForm()
        return context


class ResultView(View):
    template_name = 'research/result.html'

    def get(self, request, *args, **kwargs):

        # if it's user's research (keywords submitting) :
        if request.GET:
            context = subr.researchs_in_db(research_keywords=request.GET.get('research'))

        # when user's research had returned several foods and user had selected one
        elif kwargs:
            context = {}
            if str(request.user) != "AnonymousUser":
                # Add user's bookmarks in the context (to replace the "Sauvegarder" button by "Sauvegardé 🗹" text)
                context.update({"bookmarks": bdh.list_user_bookmarks_barcodes(str(request.user))})

            context.update(subr.researchs_in_db(food_barcode=kwargs['selected_food']))

        return render(request, self.template_name, context)


class FoodView(DetailView):
    template_name = 'research/food.html'
    model = Food
    context_object_name = 'food'
