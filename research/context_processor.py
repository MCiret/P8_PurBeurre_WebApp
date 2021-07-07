from research.forms import ResearchForm


def research_form(request):
    """ Context processor """
    return {
        "research_form": ResearchForm()

    }
