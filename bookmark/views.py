from django.shortcuts import redirect
from django.views.generic import ListView, View
import bookmark.bookmarks_db_handler as bdh


class BookmarkView(ListView):
    template_name = 'bookmark/bookmark.html'
    context_object_name = 'bookmarks_list'

    def get_queryset(self):
        return bdh.get_user_bookmarks(str(self.request.user))


class AddBookmarkView(View):

    def get(self, request, *args, **kwargs):

        if request.GET:
            bdh.save_bookmark(str(request.user), request.GET.get('bookmark_food_barcode'))

        # Always redisplay the same result page (substitute food products) after user bookmarked one of them
        return redirect('research:result-page', selected_food=kwargs['selected_food'])
