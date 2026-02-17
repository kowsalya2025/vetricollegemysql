# lms/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Course pages
    path('courses/', views.all_courses, name='all_courses'),
    path('courses/category/<slug:category_slug>/', views.courses_by_category, name='courses_by_category'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/initiate-purchase/', views.initiate_purchase, name='initiate_purchase'),
    path('courses/<slug:slug>/checkout/', views.checkout, name='checkout'),

    # My Courses
    path('my-courses/', views.my_courses, name='my_courses'),

    # Payment
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),

    # Other pages
    path("about/", views.about_us, name="about_us"),
    path('contact/', views.contact_view, name='contact'),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("terms-of-use/", views.terms_of_use, name="terms_of_use"),

    # Enroll & Purchase
    path('enroll/<slug:slug>/', views.enroll_course, name='enroll_course'),
    path('payment/<int:purchase_id>/', views.payment_page, name='payment_page'),
    path('payment/<int:purchase_id>/complete/', views.complete_payment, name='complete_payment'),

    # Video URLs
    path('video/<int:video_id>/', views.video_player, name='video_player'),
    path('video/<int:video_id>/complete/', views.mark_video_complete, name='mark_video_complete'),
    path('video/<int:video_id>/progress/', views.update_video_progress, name='update_video_progress'),

    # Quiz
    path('course/<slug:course_slug>/quiz/', views.quiz_start, name='quiz_start'),
    path('course/<slug:course_slug>/quiz/take/', views.quiz_take, name='quiz_take'),
  
    path('quiz/attempt/<int:attempt_id>/submit/', views.quiz_submit, name='quiz_submit'),
    path('quiz/attempt/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),

    # Achievement and Certificate
    path('achievements/', views.my_achievements, name='my_achievements'),
    path('certificate/<str:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    # path('checkout/<slug:slug>/', views.checkout, name='checkout'),
    # path('stripe-checkout/<slug:slug>/', views.stripe_checkout, name='stripe_checkout'),
    # path('payment/success/', views.payment_success, name='payment_success'),
    # # path('certificate/download/<int:pk>/', views.download_certificate, name='download_certificate'),
    # path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('certificate/download/<str:certificate_id>/', views.download_certificate, name='download_certificate'),
  

    # Placeholder pages 
    path('contact/', views.placeholder_view, {'page_name': 'contact'}, name='contact'), 
    path('privacy/', views.placeholder_view, {'page_name': 'privacy'}, name='privacy'),
      path('terms/', views.placeholder_view, {'page_name': 'terms'}, name='terms'),

    path('course/<slug:slug>/download-brochure/', 
         views.download_brochure, 
         name='download_brochure'),

    path('fix-images-now/', views.fix_images, name='fix_images'),


    path('checkout/<slug:slug>/', views.checkout, name='checkout'),
path('create-razorpay-order/<slug:slug>/', views.create_razorpay_order, name='create_razorpay_order'),
path('verify-payment/', views.verify_payment, name='verify_payment'),
path('payment-success/', views.payment_success, name='payment_success'),
path('payment-failed/', views.payment_failed, name='payment_failed'),
path('test-payment/<slug:slug>/', views.create_test_payment, name='create_test_payment'),
]
