from django.http import HttpResponse, HttpResponseRedirect,HttpResponseNotFound, JsonResponse
from django.core import serializers
from django.shortcuts import render
from django.urls import reverse
from book.models import Book
from django.contrib.auth.decorators import login_required
from user_profile.models import User
from .models import Review
from .forms import ReviewForm
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote
from django.db.models import Count, Avg


# Create your views here.
def get_reviews(request):
    reviews = Review.objects.all()
    books = Book.objects.all()
    top_books = Book.objects.annotate(num_reviews=Count('review')).order_by('-num_reviews')[:10]
    authors = {book.author for book in books}
    authors = list(authors)
    authors.sort()
    context = {
        'reviews' : reviews,
        'books' : books,
        'authors' : authors,
        'top_books' : top_books,
    }
    return render(request, 'main.html', context)

def see_review(request, id):
    book = Book.objects.get(pk=id)
    # Calculate the average rating for the specific book
    average_rating = Review.objects.filter(book_id=id).aggregate(Avg('rating'))

    # The average rating is stored in the dictionary as 'rating__avg'
    avg_rating_value = average_rating['rating__avg']
    context = {
        'book':book,
        'user': request.user,
        'average_rating':avg_rating_value
    }
    return render(request, 'see_review.html', context)

@login_required
def write_review(request, book_id):
    book = Book.objects.get(pk=book_id)
    context = {
        'book':book,
        'user': request.user
    }
    return render(request, 'write_review.html', context)

def get_all_reviews(request):
    reviews = Review.objects.all()
    return HttpResponse(serializers.serialize('json', reviews), content_type="application/json")

def get_reviews_by_id(request, id):
    book = Book.objects.get(pk=id)
    reviews = Review.objects.filter(book=book)
    return HttpResponse(serializers.serialize('json', reviews), content_type="application/json")

def get_reviews_by_user(request,user_id):
    reviews = Review.objects.filter(user=user_id)
    return HttpResponse(serializers.serialize('json', reviews), content_type="application/json")

def get_user(request, id):
    user = User.objects.filter(pk=id)
    return HttpResponse(serializers.serialize('json', user), content_type="application/json")

@csrf_exempt
def post_review(request, book_id):
    book = Book.objects.get(pk=book_id)
    print(request.POST)
    if request.method == 'POST':
        title = request.POST.get("title")
        content = request.POST.get("content")
        rating = request.POST.get("rating")
        user = request.user

        new_review = Review(
            title=title,
            content=content,
            rating=rating,
            user=user,
            book=book,
        )
        new_review.save()
        url = reverse('review:see_review', args=[book_id])
        print('halo',url)
        return HttpResponseRedirect(url)
    
    return HttpResponseNotFound()

@csrf_exempt
def delete_review(request,review_id):
    if request.method=='DELETE':
        review = Review.objects.get(pk=review_id)
        review.delete()

        return HttpResponse(b'DELETED', status=200)
    return HttpResponseNotFound()

def get_books_by_author(request,author):
    filteredBooks = Book.objects.filter(author=unquote(author))
    return HttpResponse(serializers.serialize('json', filteredBooks), content_type='application/json')

def get_books_by_id(request,book_id):
    filteredBooks = Book.objects.filter(pk=book_id)
    return HttpResponse(serializers.serialize('json', filteredBooks), content_type='application/json')

def get_ranks(request):
    top_books = Book.objects.annotate(num_reviews=Count('review')).order_by('-num_reviews')[:10]
    return HttpResponse(serializers.serialize('json', top_books), content_type='application/json')

def get_rating_ranks(request):
    average_ratings = Book.objects.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')[:10]
    books_data = [{'title': book.title, 'author': book.author, 'avg_rating': book.avg_rating,'id':book.pk} for book in average_ratings]
    return JsonResponse(books_data, safe=False)
