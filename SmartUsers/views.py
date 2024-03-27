import base64
import hashlib
import json
import jwt
import uuid
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
from rest_framework import generics
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomUserSerializer
import jwt

def serverStart(request):
    return HttpResponse('<h1>server started</h1>')

class FetchUserData(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decode the refresh token to get the user ID
            decoded_token = jwt.decode(refresh_token, options={"verify_signature": False})
            user_id = decoded_token.get('user_id')
            if not user_id:
                raise ValueError("User ID not found in the token.")
            
            # Now you can fetch the user object using the user ID
            user = CustomUser.objects.get(id=user_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer = CustomUserSerializer(user)
        user_data = user_serializer.data
        if user.is_staff:
            message = 'admin'
        elif user.is_student:
            message = 'student'
        elif user.is_tutor:
            message = 'tutor'

        # Generate a new access token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        data = {
            'refresh': str(refresh),
            'access': access_token,
            'user': user_data,
            'message': message
        }

        return Response(data, status=status.HTTP_200_OK)

    
class CustomUserCreateView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TutorCreateView(APIView):
    def post(self, request):
        serializer = TutorCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    serializer_class = CustomUserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    user_serializer = CustomUserSerializer(user)
                    user_data = user_serializer.data
                    if user.is_staff:
                        message = 'admin'
                    elif user.is_student:
                        message = 'student'
                    elif user.is_tutor:
                        message = 'tutor'

                    data = {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': user_data,
                        'message': message
                    }
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)
            else:   
                return Response({'message': 'Invalid Credential'}, status=status.HTTP_401_UNAUTHORIZED)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        

class CreateCategoryView(APIView):
    def post(self, request):
        category_name = request.data.get('name')
        existing_category = Category.objects.filter(name=category_name).first()
        
        if existing_category:
            return Response({"detail": "Category already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateSubCategoryView(APIView):
    def post(self, request):
        subcategory_name = request.data.get('name')
        existing_subcategory = Subcategory.objects.filter(name=subcategory_name).first()       
        if existing_subcategory:
            return Response({"detail": "Subcategory already exists"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SubcategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateCourseView(APIView):
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class SubCategoryListView(generics.ListAPIView):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class CourseListView(APIView):
    def get(self, request, id):
        courses = Course.objects.filter(tutor_id=id)
        serializer = FullCourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AdminCourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = FullCourseSerializer

class HomeCourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(isApproved = True)
    serializer_class = FullCourseSerializer
    
class CourseDetailView(APIView):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
            serializer = FullCourseSerializer(course)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
        
class CreateVideoView(APIView):
    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VideosByCourseId(APIView):
    def get(self, request, course_id):
        try:
            videos = Video.objects.filter(course_id=course_id)
            serializer = VideoSerializer(videos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Video.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)
        
class UserEditAPIView(APIView):
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AllUsersExceptOne(APIView):
    def get(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        other_users = CustomUser.objects.exclude(id=id).exclude(is_superuser=True)
        
        serializer = CustomUserSerializer(other_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CountsView(APIView):
    def get(self, request):
        user_count = CustomUser.objects.filter(is_student=True, is_staff=False).count()
        tutor_count = CustomUser.objects.filter(is_tutor=True).count()
        course_count = Course.objects.count()
        data = {
            'user_count': user_count,
            'tutor_count': tutor_count,
            'course_count': course_count
        }
        return Response(data, status=status.HTTP_200_OK)
    
class StudentListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_staff=False, is_student=True)
    serializer_class = CustomUserSerializer

class TutorListView(generics.ListAPIView):
    queryset = CustomUser.objects.filter(is_staff=False, is_tutor=True)
    serializer_class = CustomUserSerializer

class UserBlockView(generics.CreateAPIView):
    def put(self, request, id):
        try:
            user = CustomUser.objects.get(pk=id)
            user.is_active = not user.is_active 
            user.save()

            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

class CourseStatusView(APIView):
    def put(self, request, id):
        try:
            course = Course.objects.get(pk=id)
            course.isApproved = not course.isApproved 
            course.save()

            serializer = CourseSerializer(course)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
class TutorStatusView(generics.CreateAPIView):
    def put(self, request, id):
        try:
            user = CustomUser.objects.get(pk=id)
            user.is_approved = not user.is_approved 
            user.save()

            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        

class CreateCartItemView(APIView):
    def post(self, request):
        course_id = request.data.get('course')
        if CartItem.objects.filter(user=request.data.get("user"), course_id=course_id).exists():
            return Response({"message": "Course is already in the cart"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CartItemsByUser(APIView):
    def get(self, request, id):
        try:
            user_cart_items = CartItem.objects.filter(user = id)
        except CartItem.DoesNotExist:
            return Response({"message": "Cart items not found for the user"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartItemDetailSerializer(user_cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RemoveCartItemView(APIView):
    def delete(self, request, user_id, course_id):
        try:
            cart_item = CartItem.objects.get(user_id=user_id, course_id=course_id)
        except CartItem.DoesNotExist:
            return Response({"message": "Cart item not found for the user and course"}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item.delete()
        return Response({"message": "Course removed from cart successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class RemoveAllItemOfUser(APIView):
    def delete(self, request, user_id):
        try:
            cart_items = CartItem.objects.filter(user_id = user_id)
        except CartItem.DoesNotExist: 
            return Response({"message": "CartItems not found for the user"}, status=status.HTTP_404_NOT_FOUND)
        cart_items.delete()
        return Response({"message": "Items removed from cart successfully"}, status=status.HTTP_204_NO_CONTENT)
    
def generate_phonepe_payload():
    transaction = "tr-" + str(uuid.uuid4())[-6:]
    payload = {
        "merchantId": "PGTESTPAYUAT",
        "merchantTransactionId": transaction,  
        "merchantUserId": "MUID-" + str(uuid.uuid4())[-6:],
        "amount": 100000,  
        "redirectUrl": "https://oddityfinds.shop/paymentstatus/",
        "redirectMode": "POST",
        "callbackUrl": "https://oddityfinds.shop/paymentstatus/",
        "mobileNumber": "9999999999",
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }
    payload_json = json.dumps(payload)
    encoded_payload = base64.b64encode(payload_json.encode()).decode()
    salt_key = "099eb0cd-02cf-4e2a-8aca-3e6c6aff0399"
    salt_index = 1
    data_to_hash = encoded_payload + "/pg/v1/pay" + salt_key
    hashed_data = hashlib.sha256(data_to_hash.encode()).hexdigest()
    header_value = hashed_data + "###" + str(salt_index)
    

    return encoded_payload, header_value

@csrf_exempt
def PhonepePayment(request, id):
    encoded_payload, header_value = generate_phonepe_payload()
    url = "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay"
    headers = {
        'Content-Type': 'application/json',
        'X-VERIFY': header_value,
        'accept': 'application/json',
    }
    json_data = {
        'request': encoded_payload,
    }
    response = requests.post(url, headers=headers, json=json_data)
    
    if response.status_code == 200:
        responseData = response.json()
        redirect_url = responseData.get('data', {}).get('instrumentResponse', {}).get('redirectInfo', {}).get('url', '')
        print(redirect_url)
        if redirect_url:
            return JsonResponse({'redirect_url': redirect_url})
        else:
            return JsonResponse({'error': 'Redirect URL not found in response.'}, status=500)
    else:
        return JsonResponse({'error': 'Failed to process payment.'}, status=response.status_code)
    
class CreateOrderView(APIView):
    def post(self, request, user_id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        cart_items = CartItem.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        order_data = {
            "user": user.id,
            "order_items": [{"course": cart_item.course.id, "item_price": cart_item.course.fee, "is_paid" : True} for cart_item in cart_items]
        }

        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            serializer.save()
            cart_items.delete()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@csrf_exempt
def handle_phonepe_response(request):
    if request.method == 'POST':
        if not request.POST:
            return JsonResponse({'error': 'Request body is empty'}, status=400)
        transaction_id = request.POST.get('transactionId')
        status = request.POST.get('code')
        print(request.POST)
        if status == 'PAYMENT_SUCCESS':
            return redirect('https://smartstudy-frontend.vercel.app/paymentstatus?message=success')
        else:
            return redirect('https://smartstudy-frontend.vercel.app/paymentstatus?message=failed')
    else:
        return HttpResponse('Method not allowed', status=405)
    
class UserOrderItemListView(generics.ListAPIView):
    serializer_class = OrderItemDetailSerializer
    queryset = OrderItem.objects.all()

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        return self.queryset.filter(order__user_id=user_id)
    
class CheckCoursePurchaseView(generics.RetrieveAPIView):
    def get(self, request, user_id, course_id):
        has_purchased = OrderItem.objects.filter(order__user_id=user_id, course_id=course_id).exists()
        return Response({"has_purchased": has_purchased}, status=status.HTTP_200_OK)


class CoursesByCategory(APIView):
    def get(self, request, category_id):
        courses = Course.objects.filter(category_id=category_id, isApproved = True)
        serializer = FullCourseSerializer(courses, many=True)
        return Response(serializer.data)
    
class UserPasswordChange(APIView):
    def put(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            raise NotFound("User not found.")

        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            return Response({"error": "Please provide old password, new password, and confirm password."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "New password and confirm password do not match."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({"error": "Invalid old password."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

class UpdateProfilePictureAPIView(APIView):
    def put(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = CustomUserSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OrderItemByTutorAPIView(APIView):
    def get(self, request, tutor_id): 
        users = CustomUser.objects.filter(order__orderitem__course__tutor_id=tutor_id).distinct()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
