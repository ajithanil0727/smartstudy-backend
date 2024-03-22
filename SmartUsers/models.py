from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    is_tutor = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_approved = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
class Category(models.Model):
    name = models.CharField(max_length=100)

class Subcategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover = models.ImageField(upload_to='main_cover/', null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    isAvailable = models.BooleanField(default=True)
    isDeleted = models.BooleanField(default=False)
    isApproved = models.BooleanField(default=False)


class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='video_thumb/', null=True, blank=True)
    video = models.FileField(upload_to='video_file/', null=True, blank=True)
    duration = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    request = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Cancelled', 'Cancelled'), ('Approved', 'Approved')], null=True, blank=True)

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def items(self):
        return self.orderitem_set.all()

    def update_total_price(self):
        total_price = sum(item.item_price for item in self.items)
        self.total_price = total_price
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)  
    course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.update_total_price()
