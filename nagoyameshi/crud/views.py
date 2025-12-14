from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy 
from django.db.models import Q
from .models import Category, Restaurant, User, Review, Reservation, Favorite
from .forms import SignupForm, ReviewForm, ReservationForm, UserEditForm
from django.http import HttpResponseRedirect
import stripe
from django.conf import settings

# 有料会員のみアクセスを許可
class OnlyPaidUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_paid

    def handle_no_permission(self):
        return redirect('crud:settings')

class TopView(TemplateView):
    template_name = "crud/top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["new_restaurants"] = Restaurant.objects.order_by('-created_at')[:6]
        return context

class RestaurantListView(ListView):
    model = Restaurant
    template_name = "crud/restaurant_list.html"
    paginate_by = 10

    def get_queryset(self):
        query = super().get_queryset()
        keyword = self.request.GET.get('keyword')
        if keyword:
            query = query.filter(
                Q(name__icontains=keyword) | Q(address__icontains=keyword)
            )
        category_id = self.request.GET.get('category')
        if category_id:
            query = query.filter(category_id=category_id)
        order = self.request.GET.get('order')
        if order == 'price_asc':
            query = query.order_by('price_lower')
        elif order == 'price_desc':
            query = query.order_by('-price_lower')
        else:
            query = query.order_by('-created_at')
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['keyword'] = self.request.GET.get('keyword', '')
        context['category_id'] = self.request.GET.get('category', '')
        context['order'] = self.request.GET.get('order', '')
        context['total_count'] = self.get_queryset().count()
        return context

class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = "crud/restaurant_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = self.object.review_set.order_by('-created_at')
        if self.request.user.is_authenticated:
            context['is_favorite'] = Favorite.objects.filter(
                user=self.request.user, 
                restaurant=self.object
            ).exists()
        return context

class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'crud/signup.html'
    success_url = reverse_lazy('crud:top')

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'crud/review_form.html'
    
    def form_valid(self, form):
        review = form.save(commit=False)
        review.restaurant_id = self.kwargs['pk'] 
        review.user = self.request.user     
        review.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('crud:restaurant_detail', kwargs={'pk': self.kwargs['pk']})

class ReservationCreateView(OnlyPaidUserMixin, LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'crud/reservation_form.html'
    
    def form_valid(self, form):
        reservation = form.save(commit=False)
        reservation.restaurant_id = self.kwargs['pk']
        reservation.user = self.request.user
        reservation.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('crud:top')

class MypageView(LoginRequiredMixin, TemplateView):
    template_name = 'crud/mypage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservations'] = Reservation.objects.filter(user=self.request.user).order_by('-reservation_date')
        context['reviews'] = Review.objects.filter(user=self.request.user).order_by('-created_at')
        context['favorites'] = Favorite.objects.filter(user=self.request.user).order_by('-created_at')
        return context
    
class FavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        restaurant = Restaurant.objects.get(pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)
        if not created:
            favorite.delete()
        return HttpResponseRedirect(reverse_lazy('crud:restaurant_detail', kwargs={'pk': pk}))

class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'crud/user_edit.html'
    success_url = reverse_lazy('crud:mypage')

    def get_object(self):
        return self.request.user    

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'crud/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_paid'] = self.request.user.is_paid
        return context

class CheckoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse_lazy('crud:success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse_lazy('crud:settings')),
        )
        return HttpResponseRedirect(checkout_session.url)

class SuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'crud/success.html'
    
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('session_id')
        user = self.request.user

        if session_id:
            try:
                stripe.api_key = settings.STRIPE_SECRET_KEY
                session = stripe.checkout.Session.retrieve(session_id)
                user.stripe_customer_id = session.customer 
                user.is_paid = True
                user.save()
            except Exception as e:
                print(f"エラー: {e}")
        
        return super().get(request, *args, **kwargs)

class PortalView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        
        if not user.stripe_customer_id:
             return redirect('crud:settings')

        stripe.api_key = settings.STRIPE_SECRET_KEY

        portalSession = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=request.build_absolute_uri(reverse_lazy('crud:settings')),
        )
        return HttpResponseRedirect(portalSession.url)