from research.forms import ResearchForm


def research_form(request):
    """ Context processor used to have the research form in all pages header """
    return {
        "hd_research_form": ResearchForm(auto_id=False)
    }
