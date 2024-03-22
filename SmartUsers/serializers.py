from rest_framework import serializers
from .models import *


# Serializer for creating User in CustomUserModel as Student
class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'profile_picture', 'is_student', 'is_tutor', 'is_active', 'is_approved']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

# Serializer for creating user in CustomUserModel as Tutor    
class TutorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'profile_picture']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        validated_data['is_student'] = False
        validated_data['is_tutor'] = True
        validated_data['is_approved'] = False
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
# Serialzer for creating Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

# Serialzer for creating SubCategory
class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']

# Serialzer for creating Course
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover', 'fee', 'tutor', 'category', 'subcategory', 'isAvailable', 'isDeleted', 'isApproved']

# Serializer for creating Video
class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'course', 'title', 'description', 'thumbnail', 'video', 'duration', 'request']

class ChatUsersSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'get_full_name', 'image']

class FullCourseSerializer(serializers.ModelSerializer):
    tutor = TutorCreateSerializer()
    category = CategorySerializer()
    subcategory = SubcategorySerializer()
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'cover', 'fee', 'tutor', 'category', 'subcategory', 'isAvailable', 'isDeleted', 'isApproved']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'course']

class CartItemDetailSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer() 
    course = CourseSerializer() 
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'course']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['course', 'item_price', 'is_paid']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ['user', 'order_date', 'total_price', 'order_items']
        read_only_fields = ['total_price']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

class OrderItemDetailSerializer(serializers.ModelSerializer):
    course = FullCourseSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'item_price', 'is_paid']

class OrderDetailSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer() 
    items = OrderItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date', 'total_price', 'items']