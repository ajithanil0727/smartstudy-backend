from django.urls import path
from SmartUsers.views import *

urlpatterns = [
    path("", serverStart),
    path('fetchuserdata/', FetchUserData.as_view(), name='fetchuserdata'),
    path('createuser/', CustomUserCreateView.as_view(), name='createuser'),
    path('createtutor/', TutorCreateView.as_view(), name='createtutor'),
    path('userlogin/', UserLoginView.as_view(), name='userlogin'),
    path('createcategory/', CreateCategoryView.as_view(), name='createcategory'),
    path('createsubcategory/', CreateSubCategoryView.as_view(), name='createsubcategory'),
    path('createcourse/', CreateCourseView.as_view(), name='createcourse'),
    path('categorylist/', CategoryListView.as_view(), name='categorylist'),
    path('subcategorylist/', SubCategoryListView.as_view(), name='subcategorylist'),
    path('courselist/<int:id>/', CourseListView.as_view(), name='courselist'),
    path('coursesdetail/<int:course_id>/', CourseDetailView.as_view(), name='coursedetail'),
    path('categorycourse/<int:category_id>/', CoursesByCategory.as_view(), name='categorycourse'),
    path('createvideo/', CreateVideoView.as_view(), name='createvideo'),
    path('videolist/<int:course_id>/', VideosByCourseId.as_view(), name='videolist'),
    path('edituser/<int:pk>/', UserEditAPIView.as_view(), name='useredit'),
    path('changeuserpassword/<int:pk>/', UserPasswordChange.as_view(), name='changeuserpassword'),
    path('changeuserprofilepic/<int:pk>/', UpdateProfilePictureAPIView.as_view(), name='changeuserprofilepic'),
    path('getusers/<int:id>/', AllUsersExceptOne.as_view(), name='getusers'),
    path('count/', CountsView.as_view(), name='count'),
    path('studentlist/', StudentListView.as_view(), name='studentlist'),
    path('tutorlist/', TutorListView.as_view(), name='tutorlist'),
    path('admincourselist/', AdminCourseListView.as_view(), name='admincourselist'),
    path('blockuser/<int:id>/', UserBlockView.as_view(), name='userblock'),
    path('courseapprove/<int:id>/', CourseStatusView.as_view(), name='courseapprove'),
    path('tutorapprove/<int:id>/', TutorStatusView.as_view(), name='tutorapprove'),
    path('homecourselist/', HomeCourseListView.as_view(), name='homecourselist'),
    path('cartitemcreate/', CreateCartItemView.as_view(), name='cartitemcreate'),
    path('cartitems/<int:id>', CartItemsByUser.as_view(), name='cartitems'),
    path('removecartitem/<int:user_id>/<int:course_id>/', RemoveCartItemView.as_view(), name='removecartitem'),
    path('deletecartitems/<int:user_id>', RemoveAllItemOfUser.as_view(), name='deletecartitems'),
    path('pay/<int:id>/', PhonepePayment, name='pay'),
    path('paymentstatus/', handle_phonepe_response, name='paymentstatus'),
    path('ordercreate/<int:user_id>/', CreateOrderView.as_view(), name='ordercreate'),
    path('userorderlist/<int:user_id>/', UserOrderItemListView.as_view(), name='userorderlist'),
    path('checkcoursepurchase/<int:user_id>/<int:course_id>/', CheckCoursePurchaseView.as_view(), name='checkcoursepurchase'),
    path('purchasedusers/<int:tutor_id>/', OrderItemByTutorAPIView.as_view(), name='purchasedusers'),
]


 
