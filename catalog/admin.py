from django.contrib import admin
from .models import Author, Book, BookInstance, Genre, Language

# Register your models here.


class BookInline(admin.TabularInline):
    model = Book
    extra = 0


@admin.register(Author)  # admin.site.register(Author, AuthorAdmin)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]


# admin.site.register(Author)
# admin.site.register(Book)
# admin.site.register(BookInstance)
# admin.site.register(Genre)
admin.site.register(Language)

# Register the Admin classes for Book using the decorator


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )

# Register the Admin classes for Genre using the decorator


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass
