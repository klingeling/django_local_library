from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Book, BookInstance, Author
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime

from .forms import RenewBookForm

# Create your views here.


@login_required(redirect_field_name='redirect_to', login_url='/accounts/login/')
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'catalog/index.html',
        context={'num_books': num_books,
                 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors,
                 'num_visits': num_visits},  # num_visits appended
    )


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian"""
    book_inst = get_object_or_404(BookInstance, pk=pk)
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_data']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.datetime.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_data': proposed_renewal_date})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})


class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    paginate_by = 10
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    # context_object_name = 'book_list'  # your own name for the list as a template variable

    # queryset = Book.objects.filter(title__icontains='war')[:5]
    # template_name = 'books/my_arbitrary_template_name_list.html'  # Specify your own template name/location

    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='lian')[:5]  # Get 5 books containing the title war
    #
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = "This is just some data"
    #     return context


class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    # context_object_name = 'book_detail'


class AuthorListView(LoginRequiredMixin, generic.ListView):
    model = Author
    paginate_by = 10
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'


class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
    model = Author
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user. """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class StaffListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_staff.html'
    permission_required = 'catalog.can_mark_returned'


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'
    # initial = {'date of death': '02/07/2020'}


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'
