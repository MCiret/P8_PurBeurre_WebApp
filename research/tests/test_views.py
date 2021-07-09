# doc° to test view : https://docs.djangoproject.com/fr/3.2/intro/tutorial05/#test-a-view

# for ResultView() :
#
# to test if request.GET:
# client.get(reverse('research:form-page'), {'research': "nutella"})

# to test elif self.kwargs:
# client.get(reverse('research:result-page', kwargs={'selected_food': "barcode.."}))
#
# -> see doc° for the next steps ...
