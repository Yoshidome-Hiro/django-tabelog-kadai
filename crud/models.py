from django.db import models
from django.contrib.auth.models import AbstractUser  

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="カテゴリ名")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=200, verbose_name="店舗名")
    image = models.ImageField(upload_to='restaurant_images/', verbose_name="店舗画像", blank=True, null=True)
    description = models.TextField(verbose_name="説明")
    price_lower = models.PositiveIntegerField(verbose_name="価格下限")
    price_upper = models.PositiveIntegerField(verbose_name="価格上限")
    opening_time = models.CharField(max_length=100, verbose_name="営業時間")
    closing_day = models.CharField(max_length=100, verbose_name="定休日")
    address = models.CharField(max_length=200, verbose_name="住所")
    phone_number = models.CharField(max_length=20, verbose_name="電話番号")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="カテゴリ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return self.name

class User(AbstractUser):
    pass
    is_paid = models.BooleanField(default=False, verbose_name="有料会員")
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)

class Review(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name="店舗")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="会員")
    score = models.PositiveIntegerField(default=3, verbose_name="評価点数")
    comment = models.TextField(verbose_name="コメント")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.restaurant.name} - {self.user.username}"

class Reservation(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name="店舗")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="会員")
    reservation_date = models.DateTimeField(verbose_name="予約日時")
    number_of_people = models.PositiveIntegerField(verbose_name="予約人数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    def __str__(self):
        return f"{self.restaurant.name} - {self.reservation_date}"

class Favorite(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name="店舗")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="会員")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    def __str__(self):
        return f"{self.user.username} -> {self.restaurant.name}"