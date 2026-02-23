from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from urllib3 import request
from .models import Instructor
from .models import HomeBanner
from .models import Testimonial, FAQ
from .models import (
    HeroSection,  
    Course, 
    CourseEnrollment,
    FeatureSection, 
    HomeAboutSection, 
    CourseCategory,  
    Payment,
    CurriculumDay,
    Video,
    Purchase,
    UserVideoProgress
)

import json
import uuid

# Get User model
User = get_user_model()

import stripe
from django.conf import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# ===== AUTHENTICATION VIEWS =====
def home(request):
    """Home page view with hero section, categories, and featured courses"""
    hero = HeroSection.objects.filter(is_active=True).first()
    feature_section = FeatureSection.objects.filter(is_active=True).first()
    about_section = HomeAboutSection.objects.filter(is_active=True).first()
    
    categories = CourseCategory.objects.filter(is_active=True).order_by('order')
    banner = HomeBanner.objects.filter(is_active=True).first() 
    instructors = Instructor.objects.all()
    testimonials = Testimonial.objects.filter(is_active=True)
    faqs = FAQ.objects.filter(is_active=True)
    
    # Try to get featured courses, fall back to regular courses
    featured_courses = Course.objects.filter(is_active=True)
    
    # Check if Course model has is_featured field
    if hasattr(Course, 'is_featured'):
        featured_courses = featured_courses.filter(is_featured=True)
    
    featured_courses = featured_courses.order_by('-created_at')[:16]
    
    if featured_courses.count() < 16:
        additional_courses = Course.objects.filter(
            is_active=True
        ).exclude(
            id__in=[c.id for c in featured_courses]
        ).order_by('-created_at')[:16 - featured_courses.count()]
        courses = list(featured_courses) + list(additional_courses)
    else:
        courses = featured_courses
    
    all_courses_count = Course.objects.filter(is_active=True).count()
    
    context = {
        'hero': hero,
        'feature_section': feature_section,
        'about_section': about_section,
        'categories': categories,
        'courses': courses,
        'all_courses_count': all_courses_count,
        'banner': banner,
        'instructors': instructors,
        'testimonials': testimonials,
        'faqs': faqs,
    }
    return render(request, 'lms/home.html', context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please enter both email and password!')
            return redirect('login')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            # Authenticate with username (which is email in your signup)
            auth_user = authenticate(request, username=user.username, password=password)
            
            if auth_user is not None:
                login(request, auth_user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome back, {auth_user.first_name or auth_user.username}!')
                next_url = request.GET.get('next')
                return redirect(next_url or 'home')
            else:
                messages.error(request, 'Invalid email or password!')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email!')
            return redirect('login')
    
    return render(request, 'lms/login.html')


def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not all([name, email, password, confirm_password]):
            messages.error(request, 'All fields are required!')
            return redirect('signup')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('signup')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('signup')
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            # Authenticate and login the user
            auth_user = authenticate(request, username=email, password=password)
            if auth_user:
                login(request, auth_user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome {name}! Account created successfully!')
                return redirect('home')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('signup')
    
    return render(request, 'lms/signup.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


# ===== COURSE VIEWS =====

from django.db.models import Count, Q

def all_courses(request):
    courses = Course.objects.filter(is_active=True).order_by('-created_at')

    categories = CourseCategory.objects.filter(is_active=True).annotate(
        course_count=Count(
            'courses',
            filter=Q(courses__is_active=True)
        )
    ).order_by('order')

    all_courses_count = courses.count()

    category_slug = request.GET.get('category')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    context = {
        'courses': courses,
        'categories': categories,
        'all_courses_count': all_courses_count,
        'selected_category': category_slug,
    }
    return render(request, 'courses/all.html', context)


# def all_courses(request):
#     """View for all courses page with filtering"""
#     courses = Course.objects.filter(is_active=True).order_by('-created_at')
#     categories = CourseCategory.objects.filter(is_active=True).order_by('order')
    
#     category_counts = {}
#     for category in categories:
#         category_counts[category.slug] = Course.objects.filter(
#             category=category, 
#             is_active=True
#         ).count()
    
#     all_courses_count = courses.count()
    
#     category_slug = request.GET.get('category')
#     if category_slug:
#         courses = courses.filter(category__slug=category_slug)
    
#     context = {
#         'courses': courses,
#         'categories': categories,
#         'category_counts': category_counts,
#         'all_courses_count': all_courses_count,
#         'selected_category': category_slug,
#     }
#     return render(request, 'courses/all.html', context)


def courses_by_category(request, category_slug):
    """View for courses filtered by category"""
    category = get_object_or_404(CourseCategory, slug=category_slug, is_active=True)
    courses = Course.objects.filter(category=category, is_active=True).order_by('-created_at')
    all_categories = CourseCategory.objects.filter(is_active=True).order_by('order')
    
    context = {
        'category': category,
        'courses': courses,
        'categories': all_categories,
        'selected_category': category_slug,
    }
    return render(request, 'courses/category.html', context)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch
from django.conf import settings
from .models import (
    Course, CurriculumDay, Purchase, UserVideoProgress, 
    CourseReview  # Use your existing CourseReview model
)

@require_http_methods(["GET", "POST"])
def course_detail(request, slug):
    """Display course detail page with curriculum and handle review submissions"""
    
    course = get_object_or_404(
        Course.objects.prefetch_related(
            'instructors',
            Prefetch(
                'curriculum_days',
                queryset=CurriculumDay.objects.prefetch_related('videos').order_by('order', 'day_number')
            )
        ),
        slug=slug,
        is_active=True
    )

    # Handle AJAX POST requests (Review Submission)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        action = request.POST.get('action')
        
        if action == 'submit_review':
            try:
                # Validate required fields
                name = request.POST.get('name', '').strip()
                rating = request.POST.get('rating')
                review_text = request.POST.get('review', '').strip()
                
                if not name:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Name is required'
                    })
                
                if not rating:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Please select a rating'
                    })
                
                if not review_text:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Review text is required'
                    })
                
                # Validate rating value
                try:
                    rating_value = int(rating)
                    if rating_value < 1 or rating_value > 5:
                        return JsonResponse({
                            'success': False, 
                            'error': 'Rating must be between 1 and 5'
                        })
                except ValueError:
                    return JsonResponse({
                        'success': False, 
                        'error': 'Invalid rating value'
                    })
                
                # Check if user already reviewed this course (optional)
                if request.user.is_authenticated:
                    existing_review = CourseReview.objects.filter(
                        user=request.user,
                        course=course
                    ).first()
                    
                    if existing_review:
                        return JsonResponse({
                            'success': False, 
                            'error': 'You have already reviewed this course'
                        })
                
                # Create review
                review = CourseReview.objects.create(
                    course=course,
                    name=name,
                    rating=rating_value,
                    review=review_text,
                    user=request.user if request.user.is_authenticated else None,
                    # Set to True if you don't need moderation, False if you do
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Thank you! Your review has been submitted successfully.'
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'error': f'An error occurred: {str(e)}'
                })

    # Check if user has purchased the course
    user_has_paid = False
    if request.user.is_authenticated:
        user_has_paid = Purchase.objects.filter(
            user=request.user,
            course=course,
            payment_status='completed'
        ).exists()

    # Find first accessible video for "Start Learning" button
    first_video = None
    for day in course.curriculum_days.all():
        for video in day.videos.all().order_by('order', 'id'):
            if video.is_accessible_by(request.user):
                first_video = video
                break
        if first_video:
            break

    # Prepare curriculum with video access info
    curriculum_days = []
    for day in course.curriculum_days.all():
        day_data = {
            'day_number': day.day_number,
            'title': day.title,
            'description': day.description,
            'is_free': day.is_free if hasattr(day, 'is_free') else False,
            'videos': []
        }

        for video in day.videos.all().order_by('order', 'id'):
            # Centralized access check
            is_accessible = video.is_accessible_by(request.user)

            # Check completion status
            is_completed = False
            if request.user.is_authenticated:
                progress = UserVideoProgress.objects.filter(
                    user=request.user,
                    video=video
                ).first()
                if progress:
                    is_completed = progress.is_completed

            day_data['videos'].append({
                'id': video.id,
                'title': video.title,
                'description': video.description,
                'duration': video.duration,
                'is_accessible': is_accessible,
                'is_completed': is_completed,
                'video_url': video.video_file.url if hasattr(video, 'video_file') and video.video_file else ''
            })

        curriculum_days.append(day_data)

    # Get reviews - adjust based on your CourseReview model fields
    reviews = CourseReview.objects.filter(
        course=course
    ).select_related('user').order_by('-created_at')[:10]

    context = {
        'course': course,
        'curriculum_days': curriculum_days,
        'user_has_paid': user_has_paid,
        'first_video': first_video,
        'discount_percentage': course.get_discount_percentage(),
        'skills_list': course.get_skills_list(),
        'tools_list': course.get_tools_list(),
        'reviews': reviews,
    }

    return render(request, 'courses/detail.html', context)


@login_required
def initiate_purchase(request, slug):
    """Handle purchase initiation"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if user already purchased
    existing_purchase = Purchase.objects.filter(
        user=request.user,
        course=course,
        payment_status='completed'
    ).first()
    
    if existing_purchase:
        messages.info(request, 'You have already purchased this course.')
        return redirect('course_detail', slug=slug)
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        agree_terms = request.POST.get('agree_terms')
        
        if not all([full_name, email, agree_terms]):
            messages.error(request, 'Please fill all required fields and agree to terms.')
            return redirect('course_detail', slug=slug)
        
        # Create pending purchase
        purchase = Purchase.objects.create(
            user=request.user,
            course=course,
            amount_paid=course.discounted_price,
            payment_status='pending',
            full_name=full_name,
            email=email
        )
        
        # In a real application, integrate with payment gateway here
        # For now, we'll redirect to a payment page
        return redirect('payment_page', purchase_id=purchase.id)
    
    return redirect('course_detail', slug=slug)


@login_required
def payment_page(request, purchase_id):
    """Display payment page"""
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    
    if purchase.payment_status == 'completed':
        messages.info(request, 'This purchase is already completed.')
        return redirect('course_detail', slug=purchase.course.slug)
    
    context = {
        'purchase': purchase,
        'course': purchase.course
    }
    
    return render(request, 'lms/payment_page.html', context)


# @login_required
# @require_POST
# def complete_payment(request, purchase_id):
#     """Complete the payment process"""
#     purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    
#     # In real application, verify payment with gateway
#     # For demo, we'll mark as completed
#     transaction_id = request.POST.get('transaction_id', f'TXN{purchase.id}')
    
#     purchase.payment_status = 'completed'
#     purchase.transaction_id = transaction_id
#     purchase.save()
    
#     messages.success(request, 'Payment successful! You now have access to the full course.')
#     return redirect('course_detail', slug=purchase.course.slug)

@login_required
@require_POST
def complete_payment(request, purchase_id):
    """Complete the payment process"""
    purchase = get_object_or_404(Purchase, id=purchase_id, user=request.user)
    
    transaction_id = request.POST.get('transaction_id', f'TXN{purchase.id}')
    
    purchase.payment_status = 'completed'
    purchase.transaction_id = transaction_id
    purchase.save()
    
    # ✅ Changed: redirect to success page instead of course_detail
    return redirect('payment_success', order_id=purchase.id)

@login_required
def payment_success(request, order_id):
    """Show payment success page then redirect to my courses"""
    purchase = get_object_or_404(Purchase, id=order_id, user=request.user)
    course = purchase.course

    total_amount = purchase.amount
    tax_amount = round(total_amount * 18 / 118, 2)   # extract GST
    base_price = round(total_amount - tax_amount, 2)

    context = {
        'course': course,
        'order_id': purchase.id,
        'order_date': purchase.purchased_at.strftime("%B %d, %Y"),
        'payment_method': getattr(purchase, 'payment_method', 'UPI ID'),
        'course_price': total_amount,
        'is_discounted': False,
        'discount_amount': 0,
        'base_price': base_price,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
    }
    return render(request, 'lms/payment_success.html', context)



@csrf_exempt
def save_video_progress(request, video_id):
    """Save video progress (for auto-save)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Authentication required'}, status=401)
    
    try:
        video = Video.objects.get(id=video_id)
        data = json.loads(request.body)
        watched_percentage = data.get('watched_percentage', 0)
        
        progress, created = UserVideoProgress.objects.update_or_create(
            user=request.user,
            video=video,
            defaults={
                'watched_percentage': watched_percentage
            }
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# 
@require_POST
@csrf_exempt  # Only use this for testing, remove in production or use proper CSRF handling
def mark_video_complete(request, video_id):
    """Mark a video as completed for the current user"""
    try:
        video = Video.objects.get(id=video_id)
        
        # Get or create progress record
        progress, created = UserVideoProgress.objects.get_or_create(
            user=request.user,
            video=video
        )
        
        # Mark as completed
        progress.is_completed = True
        progress.watched_percentage = 100
        progress.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Video marked as complete',
            'video_id': video_id
        })
        
    except Video.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Video not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Purchase, CourseEnrollment, CourseProgress, Certificate, Quiz


@login_required
def my_courses(request):
    """Display user's purchased and enrolled courses with first video, progress, and certificate"""
    
    # Purchases
    purchases = Purchase.objects.filter(
        user=request.user,
        payment_status='completed'
    ).select_related('course__category').prefetch_related(
        'course__instructors',
        'course__curriculum_days__videos'
    ).order_by('-purchased_at')
    
    # Legacy enrollments
    enrollments = CourseEnrollment.objects.filter(
        user=request.user
    ).select_related('course__category').prefetch_related(
        'course__instructors',
        'course__curriculum_days__videos'
    ).order_by('-enrolled_at')
    
    # Filter out enrollments that are already purchased
    purchased_course_ids = [p.course.id for p in purchases]
    enrollments = [e for e in enrollments if e.course.id not in purchased_course_ids]
    
    # Collect all course IDs for bulk fetching progress and certificates
    all_courses = [p.course for p in purchases] + [e.course for e in enrollments]
    course_ids = [c.id for c in all_courses]
    
    # Bulk fetch progress, certificates, and quizzes
    progress_map = {
        cp.course_id: cp 
        for cp in CourseProgress.objects.filter(user=request.user, course_id__in=course_ids)
    }
    certificate_map = {
        cert.course_id: cert 
        for cert in Certificate.objects.filter(user=request.user, course_id__in=course_ids)
    }
    earned_certificates = list(certificate_map.values())
    quiz_map = {
        quiz.course_id: True 
        for quiz in Quiz.objects.filter(course_id__in=course_ids)
    }
    
    # Assign first video, progress, certificate, and quiz status
    def enhance_course(obj):
        first_video = None
        for day in obj.course.curriculum_days.all().order_by('order', 'day_number'):
            videos = day.videos.all().order_by('order', 'id')
            if videos.exists():
                first_video = videos.first()
                break
        
        obj.first_video = first_video
        obj.progress = progress_map.get(obj.course.id)
        obj.certificate = certificate_map.get(obj.course.id)
        obj.has_quiz = quiz_map.get(obj.course.id, False)
    
    for p in purchases:
        enhance_course(p)
    for e in enrollments:
        enhance_course(e)
    
    # Combine purchases and enrollments for the template
    all_purchases = list(purchases) + list(enrollments)
   


    
    context = {
        'purchases': all_purchases,  # Combined list for template
        'title': 'My Courses',
        'certificates': earned_certificates, 
    }
    
    return render(request, 'lms/my_courses.html', context)



from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import Video, Course, Tool


def video_player(request, video_id):
    """
    Video player view (READ-ONLY for course & quiz state)
    Safe for GET requests – no quiz validation or writes.
    """

    # -------------------------------------------------
    # Video + course
    # -------------------------------------------------
    video = get_object_or_404(
        Video.objects.select_related("curriculum_day__course"),
        id=video_id,
    )
    

    course = video.curriculum_day.course

    tools = video.tools_needed.all() if video.tools_needed.exists() else course.tools.all()

    # -------------------------------------------------
    # Access control
    # -------------------------------------------------
    if not video.is_accessible_by(request.user):
        if not request.user.is_authenticated:
            messages.error(request, "Please login to access this video.")
            return HttpResponseRedirect(
                f"{reverse('login')}?next={request.path}"
            )

        messages.error(
            request,
            "You need to purchase the course to access this video.",
        )
        return redirect("course_detail", slug=course.slug)

    # -------------------------------------------------
    # Current video progress
    # -------------------------------------------------
    progress = None
    is_completed = False
    progress_percentage = 0
    watched_percentage = 0
    watched_duration = 0

    if request.user.is_authenticated:
        progress, _ = UserVideoProgress.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={
                "is_completed": False,
                "watched_percentage": 0,
                "watched_duration": 0,
            },
        )

        is_completed = progress.is_completed
        progress_percentage = progress.progress_percentage
        watched_percentage = progress.progress_percentage
        watched_duration = progress.watched_duration

    # -------------------------------------------------
    # Curriculum + video listing
    # -------------------------------------------------
    curriculum_days = []
    all_videos_list = []
    completed_days = 0

    curriculum_days_qs = (
        CurriculumDay.objects.filter(course=course)
        .prefetch_related("videos")
        .order_by("order", "day_number")
    )

    for day in curriculum_days_qs:
        day_videos = []
        completed_count = 0

        for vid in day.videos.all().order_by("order", "id"):
            vid_progress = None

            if request.user.is_authenticated:
                vid_progress = UserVideoProgress.objects.filter(
                    user=request.user,
                    video=vid,
                ).first()

            vid_completed = vid_progress.is_completed if vid_progress else False
            vid_percentage = (
                vid_progress.progress_percentage if vid_progress else 0
            )
            vid_duration = (
                vid_progress.watched_duration if vid_progress else 0
            )

            if vid_completed:
                completed_count += 1

            day_videos.append(
                {
                    "id": vid.id,
                    "title": vid.title,
                    "duration": vid.duration or 0,
                    "is_accessible": vid.is_accessible_by(request.user),
                    "is_completed": vid_completed,
                    "progress_percentage": vid_percentage,
                    "watched_percentage": vid_percentage,
                    "watched_duration": vid_duration,
                    "order": vid.order or 0,
                }
            )

            all_videos_list.append(vid)

        total_videos_in_day = len(day_videos)
        day_progress_percentage = (
            int((completed_count / total_videos_in_day) * 100)
            if total_videos_in_day
            else 0
        )

        if day_progress_percentage == 100:
            completed_days += 1

        curriculum_days.append(
            {
                "id": day.id,
                "title": day.title,
                "videos": day_videos,
                "completed_videos": completed_count,
                "total_videos": total_videos_in_day,
                "progress_percentage": day_progress_percentage,
            }
        )

    # -------------------------------------------------
    # Previous / Next video
    # -------------------------------------------------
    previous_video = None
    next_video = None

    try:
        idx = all_videos_list.index(video)

        if idx > 0:
            prev = all_videos_list[idx - 1]
            if prev.is_accessible_by(request.user):
                previous_video = prev

        if idx < len(all_videos_list) - 1:
            nxt = all_videos_list[idx + 1]
            if nxt.is_accessible_by(request.user):
                next_video = nxt

    except ValueError:
        pass

    # -------------------------------------------------
    # Course progress (READ ONLY)
    # -------------------------------------------------
    total_videos = len(all_videos_list)
    completed_videos = 0
    course_progress = 0

    if request.user.is_authenticated:
        completed_videos = UserVideoProgress.objects.filter(
            user=request.user,
            video__in=all_videos_list,
            is_completed=True,
        ).count()

        course_progress = (
            int((completed_videos / total_videos) * 100)
            if total_videos
            else 0
        )

    # -------------------------------------------------
    # Quiz & certificate status (NO VALIDATION)
    # -------------------------------------------------
    quiz_passed = False
    has_quiz = False
    course_completed = False
    certificate = None

    if request.user.is_authenticated:
        course_progress_obj, _ = CourseProgress.objects.get_or_create(
            user=request.user,
            course=course,
        )

        quiz_passed = course_progress_obj.quiz_passed
        course_completed = course_progress_obj.is_completed
        has_quiz = hasattr(course, "quiz") and course.quiz is not None

        if course_completed:
            certificate = Certificate.objects.filter(
                user=request.user,
                course=course,
            ).first()

        

    # -------------------------------------------------
    # Context
    # -------------------------------------------------
    context = {
        "video": video,
        "course": course,
        "progress": progress,
        "curriculum_days": curriculum_days,
        "current_day": video.curriculum_day,
        "previous_video": previous_video,
        "next_video": next_video,
        "course_progress": course_progress,
        "total_videos": total_videos,
        "completed_videos": completed_videos,
        "completed_days": completed_days,
        "is_completed": is_completed,
        "progress_percentage": progress_percentage,
        "watched_percentage": watched_percentage,
        "watched_duration": watched_duration,
        "quiz_passed": quiz_passed,
        "has_quiz": has_quiz,
        "course_completed": course_completed,
        "certificate": certificate,
        'tools': tools,
    }

    return render(request, "courses/video_player.html", context)



@login_required
def update_video_progress(request, video_id):
    video = get_object_or_404(Video, id=video_id)

    progress_percentage = int(request.POST.get('progress', 0))
    is_completed = request.POST.get('completed') == 'true'
    watched_seconds = int(request.POST.get('watched_seconds', 0))

    UserVideoProgress.objects.update_or_create(
        user=request.user,
        video=video,
        defaults={
            'progress_percentage': progress_percentage,
            'is_completed': is_completed,
            'watched_duration': watched_seconds
        }
    )

    return JsonResponse({'success': True})


@login_required
def enroll_course(request, slug):
    """Simple enrollment view"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if already enrolled
    if CourseEnrollment.objects.filter(user=request.user, course=course).exists():
        messages.info(request, f'You are already enrolled in "{course.title}"')
        return redirect('course_detail', slug=slug)
    
    if request.method == 'POST':
        CourseEnrollment.objects.create(
            user=request.user, 
            course=course,
            enrollment_type='free',
            is_paid=False
        )
        messages.success(request, f'Successfully enrolled in "{course.title}"!')
        return redirect('my_courses')
    
    context = {
        'course': course,
    }
    return render(request, 'courses/enroll.html', context)

# ========== RAZORPAY PAYMENT VIEWS ==========
import razorpay
import hmac
import hashlib
import json
import uuid
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Course, Payment, Purchase, CourseEnrollment

# Initialize Razorpay client ONCE
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# ========== CHECKOUT PAGE ==========
@login_required
def checkout(request, slug):
    """Display checkout page"""
    course = get_object_or_404(Course, slug=slug)

    course_price = float(course.original_price)
    is_discounted = False
    discount_amount = 0

    if course.discounted_price and course.discounted_price < course.original_price:
        is_discounted = True
        base_price = float(course.discounted_price)
        discount_amount = course_price - base_price
    else:
        base_price = course_price

    tax_rate = 0.18  # 18% GST
    tax_amount = base_price * tax_rate
    total_amount = base_price + tax_amount

    context = {
        'course': course,
        'course_price': course_price,
        'is_discounted': is_discounted,
        'base_price': round(base_price, 2),
        'discount_amount': round(discount_amount, 2) if is_discounted else 0,
        'tax_amount': round(tax_amount, 2),
        'total_amount': round(total_amount, 2),
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,  # ← changed from stripe
    }

    return render(request, 'courses/checkout.html', context)


# ========== CREATE RAZORPAY ORDER ==========
@login_required
def create_razorpay_order(request, slug):
    """Create Razorpay order and return order details"""
    course = get_object_or_404(Course, slug=slug)

    # Check if already purchased
    if Purchase.objects.filter(
        user=request.user,
        course=course,
        payment_status='completed'
    ).exists():
        return JsonResponse({'success': False, 'error': 'Already purchased this course'})

    original_price = float(course.original_price)
    discounted_price = float(course.discounted_price) if course.discounted_price else original_price

    is_discounted = discounted_price < original_price
    base_price = discounted_price if is_discounted else original_price

    tax_amount = base_price * 0.18
    total_amount = base_price + tax_amount

    # Razorpay needs amount in paise (smallest unit)
    amount_paise = int(round(total_amount * 100))

    print(f"=== RAZORPAY ORDER DEBUG ===")
    print(f"Course: {course.title}")
    print(f"Base Price: ₹{base_price}")
    print(f"Tax (18%): ₹{tax_amount}")
    print(f"Total: ₹{total_amount}")
    print(f"Amount in Paise: {amount_paise}")
    print(f"===========================")

    try:
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': f'receipt_{uuid.uuid4().hex[:10]}',
            'notes': {
                'course_id': str(course.id),
                'user_id': str(request.user.id),
                'course_title': course.title,
            }
        })

        # Save pending Payment record
        Payment.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                'razorpay_order_id': razorpay_order['id'],
                'amount': total_amount,
                'currency': 'INR',
                'status': 'pending',
            }
        )

        return JsonResponse({
            'success': True,
            'razorpay_order_id': razorpay_order['id'],
            'amount': amount_paise,
            'currency': 'INR',
            'course_name': course.title,
            'user_name': request.user.get_full_name() or request.user.username,
            'user_email': request.user.email,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)})


# ========== VERIFY PAYMENT ==========
@csrf_exempt
@login_required
def verify_payment(request):
    """Verify Razorpay payment signature after successful payment"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)

        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        course_id = data.get('course_id')

        # Verify signature
        msg = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            return JsonResponse({'success': False, 'error': 'Invalid payment signature'}, status=400)

        course = Course.objects.get(id=course_id)

        # Update Payment record
        Payment.objects.filter(
            user=request.user,
            razorpay_order_id=razorpay_order_id
        ).update(
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            status='success',
            payment_date=timezone.now(),
        )

        # Get payment amount
        payment = Payment.objects.get(
            user=request.user,
            razorpay_order_id=razorpay_order_id
        )

        # ✅ Capture purchase with purchase, _
        purchase, _ = Purchase.objects.update_or_create(
            user=request.user,
            course=course,
            defaults={
                'amount_paid': payment.amount,
                'payment_status': 'completed',
                'transaction_id': razorpay_payment_id,
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'purchased_at': timezone.now(),
            }
        )

        # Create Enrollment
        CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'enrollment_type': 'paid',
                'is_paid': True,
                'transaction_id': razorpay_payment_id,
            }
        )

        # ✅ Now purchase.id works
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('payment_success', kwargs={'order_id': purchase.id})
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========== PAYMENT SUCCESS PAGE ==========
"""
lms/views/payment_success.py
Payment-success view — generates invoice PDF and sends confirmation email.
"""

import logging
import datetime

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import Payment, Course, CourseEnrollment  # adjust to your actual model paths
from .utils.email_utils import send_purchase_confirmation_email

logger = logging.getLogger(__name__)

@login_required
def payment_success(request, order_id):
    purchase = get_object_or_404(Purchase, pk=order_id, user=request.user)

    email_sent_key = f"invoice_sent_{purchase.id}"
    already_sent   = request.session.get(email_sent_key, False)

    student      = request.user
    course       = purchase.course
    course_price = float(purchase.amount_paid)
    tax_amount   = round(course_price * 18 / 118, 2)
    base_price   = round(course_price - tax_amount, 2)

    order_data = {
        "order_id":        purchase.id,
        "order_date":      purchase.purchased_at.strftime("%d %b %Y"),
        "payment_method":  purchase.transaction_id or "Razorpay",
        "student_name":    purchase.full_name or student.get_full_name() or student.username,
        "student_email":   purchase.email or student.email,
        "course_title":    course.title,
        "course_price":    course_price,
        "is_discounted":   False,
        "discount_amount": 0,
        "base_price":      base_price,
        "tax_amount":      tax_amount,
        "total_amount":    course_price,
        "platform_name":   "EduLearn LMS",
        "my_courses_url":  request.build_absolute_uri(reverse("my_courses")),
        "year":            datetime.date.today().year,
    }

    if not already_sent:
        try:
            send_purchase_confirmation_email(order_data)
            request.session[email_sent_key] = True
            logger.info("Invoice email sent for purchase #%s to %s", purchase.id, student.email)
        except Exception as exc:
            logger.error("Failed to send invoice email for purchase #%s: %s", purchase.id, exc, exc_info=True)

    context = {
        "order_id":        purchase.id,
        "order_date":      order_data["order_date"],
        "payment_method":  order_data["payment_method"],
        "course":          course,
        "course_price":    course_price,
        "is_discounted":   False,
        "discount_amount": 0,
        "base_price":      base_price,
        "tax_amount":      tax_amount,
        "total_amount":    course_price,
        "email_sent":      not already_sent,
    }
    return render(request, "lms/payment_success.html", context)

"""
lms/utils/invoice_generator.py
Generate a professional PDF invoice for course purchases.
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT


# ── Brand colours ─────────────────────────────────────────────────────────────
GREEN       = colors.HexColor("#4CAF50")
DARK_GREEN  = colors.HexColor("#2E7D32")
LIGHT_GREEN = colors.HexColor("#E8F5E9")
GREY_TEXT   = colors.HexColor("#757575")
DARK_TEXT   = colors.HexColor("#212121")
WHITE       = colors.white


def _s(name, base_styles, **kw):
    """Shortcut to create a named ParagraphStyle."""
    return ParagraphStyle(name, parent=base_styles["Normal"], **kw)


def generate_invoice_pdf(order_data: dict) -> bytes:
    """
    Build a PDF invoice and return the raw bytes.

    Required keys in `order_data`:
        order_id, order_date, payment_method,
        student_name, student_email,
        course_title, course_price (float),
        is_discounted (bool), discount_amount (float),
        base_price (float), tax_amount (float), total_amount (float),
        platform_name  (optional, default "EduLearn LMS")
    """
    buffer = io.BytesIO()
    platform = order_data.get("platform_name", "Vetri Digital College")
    styles   = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
    )
    W = doc.width

    # ── Paragraph style factory ────────────────────────────────────────────────
    S = {
        "brand":   _s("brand",   styles, fontSize=22, textColor=GREEN,      fontName="Helvetica-Bold"),
        "tagline": _s("tagline", styles, fontSize=8,  textColor=GREY_TEXT),
        "invoice": _s("invoice", styles, fontSize=18, textColor=DARK_TEXT,  fontName="Helvetica-Bold", alignment=TA_RIGHT),
        "label":   _s("label",   styles, fontSize=8,  textColor=GREY_TEXT),
        "value":   _s("value",   styles, fontSize=9,  textColor=DARK_TEXT,  fontName="Helvetica-Bold"),
        "normal":  _s("normal",  styles, fontSize=9,  textColor=DARK_TEXT),
        "th":      _s("th",      styles, fontSize=8,  textColor=WHITE,      fontName="Helvetica-Bold"),
        "th_r":    _s("th_r",    styles, fontSize=8,  textColor=WHITE,      fontName="Helvetica-Bold", alignment=TA_RIGHT),
        "th_c":    _s("th_c",    styles, fontSize=8,  textColor=WHITE,      fontName="Helvetica-Bold", alignment=TA_CENTER),
        "cell_c":  _s("cell_c",  styles, fontSize=9,  textColor=DARK_TEXT,  alignment=TA_CENTER),
        "cell_r":  _s("cell_r",  styles, fontSize=9,  textColor=DARK_TEXT,  alignment=TA_RIGHT),
        "footer":  _s("footer",  styles, fontSize=7,  textColor=GREY_TEXT,  alignment=TA_CENTER),
        "thanks":  _s("thanks",  styles, fontSize=9,  textColor=GREY_TEXT,  alignment=TA_CENTER),
    }

    story = []

    # ─────────────────────────────────────────────────────────────────────────
    # 1. HEADER  (brand left | INVOICE right)
    # ─────────────────────────────────────────────────────────────────────────
    hdr = Table(
        [[Paragraph(platform, S["brand"]), Paragraph("INVOICE", S["invoice"])]],
        colWidths=[W * 0.5, W * 0.5],
    )
    hdr.setStyle(TableStyle([
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 0),
    ]))
    story.append(hdr)
    story.append(Paragraph("Online Learning Platform", S["tagline"]))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=6 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 2. ORDER META  (left: order info | right: bill-to)
    # ─────────────────────────────────────────────────────────────────────────
    def meta_block(rows):
        data = [[Paragraph(lbl, S["label"]), Paragraph(str(val), S["value"])]
                for lbl, val in rows]
        t = Table(data, colWidths=[32 * mm, 55 * mm])
        t.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t

    left_meta = meta_block([
        ("Invoice No.",    f"#{order_data['order_id']}"),
        ("Date",           order_data["order_date"]),
        ("Payment Method", order_data["payment_method"]),
        ("Status",         "Paid ✓"),
    ])
    right_meta = meta_block([
        ("Bill To", order_data["student_name"]),
        ("Email",   order_data["student_email"]),
    ])

    meta_tbl = Table([[left_meta, right_meta]], colWidths=[W * 0.5, W * 0.5])
    meta_tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 3. LINE-ITEMS TABLE
    # ─────────────────────────────────────────────────────────────────────────
    col_w = [W * 0.55, W * 0.15, W * 0.15, W * 0.15]

    items_data = [
        # Header row
        [
            Paragraph("DESCRIPTION", S["th"]),
            Paragraph("QTY",         S["th_c"]),
            Paragraph("UNIT PRICE",  S["th_r"]),
            Paragraph("AMOUNT",      S["th_r"]),
        ],
        # Single item row
        [
            Paragraph(order_data["course_title"], S["normal"]),
            Paragraph("1",                        S["cell_c"]),
            Paragraph(f"\u20b9{order_data['course_price']:,.2f}", S["cell_r"]),
            Paragraph(f"\u20b9{order_data['course_price']:,.2f}", S["cell_r"]),
        ],
    ]

    items_tbl = Table(items_data, colWidths=col_w, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  GREEN),
        ("ROWBACKGROUND", (0, 1), (-1, 1),  LIGHT_GREEN),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(items_tbl)
    story.append(Spacer(1, 4 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 4. TOTALS BLOCK  (right-aligned)
    # ─────────────────────────────────────────────────────────────────────────
    tw        = W * 0.45
    col_left  = tw * 0.55
    col_right = tw * 0.45

    def price_row(label, amount, red=False, highlight=False):
        txt_color = WHITE if highlight else (colors.HexColor("#E53935") if red else DARK_TEXT)
        fn        = "Helvetica-Bold" if highlight else "Helvetica"
        fs        = 10 if highlight else 9
        lp = _s(f"lbl_{label}", styles, fontSize=fs, textColor=txt_color, fontName=fn)
        rp = _s(f"amt_{label}", styles, fontSize=fs, textColor=txt_color, fontName=fn, alignment=TA_RIGHT)
        return [Paragraph(label, lp), Paragraph(amount, rp)]

    totals_rows = []
    if order_data.get("is_discounted"):
        totals_rows.append(price_row(
            "Original Price",
            f"\u20b9{float(order_data['course_price']):,.2f}"
        ))
        totals_rows.append(price_row(
            "Discount",
            f"-\u20b9{float(order_data['discount_amount']):,.2f}",
            red=True
        ))
    totals_rows.append(price_row("Subtotal",   f"\u20b9{float(order_data['base_price']):,.2f}"))
    totals_rows.append(price_row("GST (18%)", f"\u20b9{float(order_data['tax_amount']):,.2f}"))
    totals_rows.append(price_row("TOTAL PAID", f"\u20b9{float(order_data['total_amount']):,.2f}", highlight=True))

    last_idx = len(totals_rows) - 1
    totals_tbl = Table(totals_rows, colWidths=[col_left, col_right])
    totals_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("LINEABOVE",     (0, last_idx), (-1, last_idx), 1.5, GREEN),
        ("BACKGROUND",    (0, last_idx), (-1, last_idx), GREEN),
    ]))

    # Push totals block to the right side
    wrapper = Table([[None, totals_tbl]], colWidths=[W - tw, tw])
    wrapper.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(wrapper)
    story.append(Spacer(1, 10 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 5. FOOTER
    # ─────────────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GREEN, spaceAfter=4 * mm))
    story.append(Paragraph(
        f"Thank you for your purchase, {order_data['student_name']}! "
        "We wish you a great learning experience.",
        S["thanks"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f"Questions? Reply to this email or visit our Help Center. — {platform}",
        S["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()


# ========== PAYMENT FAILED PAGE ==========
@login_required
def payment_failed(request):
    """Payment failed page"""
    error_code = request.GET.get('error_code', 'Unknown')
    error_desc = request.GET.get('error_description', 'Payment was not completed')

    return render(request, 'courses/payment_failed.html', {
        'error_code': error_code,
        'error_desc': error_desc,
    })


# ========== TEST PAYMENT (DEBUG ONLY) ==========
@login_required
def create_test_payment(request, slug):
    """Create test payment for development only"""
    if not settings.DEBUG:
        return JsonResponse({'success': False, 'error': 'Not allowed in production'}, status=403)

    try:
        course = get_object_or_404(Course, slug=slug, is_active=True)

        if Purchase.objects.filter(
            user=request.user,
            course=course,
            payment_status='completed'
        ).exists():
            return JsonResponse({'success': False, 'error': 'Already purchased this course'})

        test_order_id = f'test_order_{uuid.uuid4().hex[:10]}'
        test_payment_id = f'test_payment_{uuid.uuid4().hex[:10]}'
        amount = float(course.discounted_price or course.original_price)

        Payment.objects.create(
            user=request.user,
            course=course,
            razorpay_order_id=test_order_id,
            razorpay_payment_id=test_payment_id,
            amount=amount,
            currency='INR',
            status='success',
            payment_method='test',
            payment_date=timezone.now(),
        )

        Purchase.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'amount_paid': amount,
                'payment_status': 'completed',
                'transaction_id': test_payment_id,
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        )

        CourseEnrollment.objects.get_or_create(
            user=request.user,
            course=course,
            defaults={
                'enrollment_type': 'paid',
                'is_paid': True,
                'transaction_id': test_payment_id,
            }
        )

        return JsonResponse({'success': True, 'redirect_url': f'/courses/{course.slug}/'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



def about_us(request):
    """About Us page"""
    return render(request, 'lms/about.html', {
        'title': 'About Us',
        'message': 'Learn more about our e-learning platform.'
    })


def placeholder_view(request, page_name=None):
    """Catch-all for pages not implemented yet"""
    page_titles = {
        'about': 'About Us',
        'contact': 'Contact Us',
        'privacy': 'Privacy Policy',
        'terms': 'Terms & Conditions',
    }
    
    title = page_titles.get(page_name, page_name.replace('-', ' ').title() if page_name else 'Page')
    
    return render(request, 'lms/placeholder.html', {
        'title': title,
        'message': f'The {title} page is coming soon!'
    })
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'lms/contact.html', {'form': form})



def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, "privacy_policy.html")


def terms_of_use(request):
    """Terms of Use page"""
    return render(request, "terms_of_use.html")



# quezz
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import (
    Quiz, QuizAttempt, QuizResponse, Question, Answer,
    CourseProgress, Certificate, Course
)

@login_required
def quiz_start(request, course_slug):
    """Display quiz instructions and start quiz"""
    course = get_object_or_404(Course, slug=course_slug)
    
    try:
        quiz = course.quiz
    except Quiz.DoesNotExist:
        messages.error(request, "This course doesn't have a quiz yet.")
        return redirect('course_detail', slug=course_slug)
    
    # -----------------------
    # Check if user has access
    # -----------------------
    has_access = (
        request.user.purchases.filter(course=course).exists() or
        request.user.enrollments.filter(course=course).exists()
    )
    
    if not has_access:
        messages.error(request, "You need to enroll in this course first.")
        return redirect('course_detail', slug=course_slug)

    # -----------------------
    # NEW: Ensure all videos completed before quiz
    # -----------------------
    if request.user.is_authenticated:
        course_progress_obj, _ = CourseProgress.objects.get_or_create(
            user=request.user,
            course=course
        )
        if course_progress_obj.progress_percentage < 100:
            messages.error(request, "You must complete all course videos before taking the quiz.")
            return redirect('course_detail', slug=course_slug)
    
    # -----------------------
    # Check previous attempts
    # -----------------------
    attempts = QuizAttempt.objects.filter(user=request.user, quiz=quiz)
    attempts_count = attempts.count()
    best_score = attempts.filter(passed=True).order_by('-score').first()
    
    # ... rest of your view ...

    
    # Check if max attempts reached
    if quiz.max_attempts > 0 and attempts_count >= quiz.max_attempts:
        if not best_score:
            messages.error(request, f"You have used all {quiz.max_attempts} attempts.")
            return redirect('course_detail', slug=course_slug)
    
    context = {
        'course': course,
        'quiz': quiz,
        'attempts_count': attempts_count,
        'attempts_left': quiz.max_attempts - attempts_count if quiz.max_attempts > 0 else None,
        'best_score': best_score,
        'total_questions': quiz.get_total_questions(),
    }
    
    return render(request, 'lms/quiz_start.html', context)


@login_required
def quiz_take(request, course_slug):
    """Take the quiz"""
    course = get_object_or_404(Course, slug=course_slug)
    quiz = get_object_or_404(Quiz, course=course)
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quiz
    )
    
    questions = quiz.questions.prefetch_related('answers').all()
    
    context = {
        'course': course,
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
    }
    
    return render(request, 'lms/quiz_take.html', context)


from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages

def quiz_submit(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)

    if request.method != "POST":
        return redirect("quiz_take", attempt.quiz.id)

    # Prevent resubmission
    if attempt.completed_at:
        messages.error(request, "This quiz attempt is already submitted.")
        return redirect("quiz_result", attempt.id)

    for question in attempt.quiz.questions.all():
        key = f"question_{question.id}"
        selected_ids = request.POST.getlist(key)

        if not selected_ids:
            continue  # unanswered question

        # Validate answers belong to this question
        answers = Answer.objects.filter(
            id__in=selected_ids,
            question=question
        )

        if not answers.exists():
            continue

        response = QuizResponse.objects.create(
            attempt=attempt,
            question=question
        )

        response.selected_answers.set(answers)

    # Mark attempt completed
    attempt.completed_at = timezone.now()
    attempt.calculate_score()

    messages.success(request, "Quiz submitted successfully.")
    return redirect("quiz_result", attempt.id)



@login_required
def quiz_result(request, attempt_id):
    """Display quiz results"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    responses = attempt.responses.prefetch_related(
        'question__answers',
        'selected_answers'
    ).all()
    
    # Prepare detailed results and count correct/incorrect
    results = []
    correct_count = 0
    incorrect_count = 0
    
    for response in responses:
        question = response.question
        correct_answers = question.answers.filter(is_correct=True)
        selected_answers = response.selected_answers.all()
        is_correct = response.is_correct()
        
        # Count correct/incorrect answers
        if is_correct:
            correct_count += 1
        else:
            incorrect_count += 1
        
        results.append({
            'question': question,
            'selected_answers': selected_answers,
            'correct_answers': correct_answers,
            'is_correct': is_correct,
        })
    
    # Calculate total questions
    total_questions = len(results)
    
    # Check if certificate was generated
    certificate = None
    if attempt.passed:
        progress = CourseProgress.objects.filter(
            user=request.user,
            course=attempt.quiz.course
        ).first()
        
        if progress and progress.is_completed:
            certificate = Certificate.objects.filter(
                user=request.user,
                course=attempt.quiz.course
            ).first()
    
    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'course': attempt.quiz.course,
        'results': results,
        'certificate': certificate,
        # Add these for the stats
        'total_questions': total_questions,
        'correct_count': correct_count,
        'incorrect_count': incorrect_count,
    }
    
    return render(request, 'lms/quiz_result.html', context)

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Video, CourseProgress, Certificate

# views.py


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
from .models import Video, CourseProgress, Certificate

@login_required
@require_POST
def mark_video_complete(request, video_id):
    """Mark a video as completed and update progress"""
    try:
        video = get_object_or_404(Video, id=video_id)
        course = video.curriculum_day.course
        
        # Get or create UserVideoProgress
        progress, created = UserVideoProgress.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={
                'is_completed': False,
                'watched_percentage': 0,
                'watched_duration': 0
            }
        )
        
        # Parse request body
        try:
            data = json.loads(request.body)
            watched_percentage = data.get('progress_percentage', 100)
        except:
            watched_percentage = 100
        
        # Update video progress
        progress.is_completed = True
        progress.watched_percentage = watched_percentage
        progress.save()
        
        # Get or create CourseProgress (for quiz tracking)
        course_progress, created = CourseProgress.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        # Add video to completed videos
        if video not in course_progress.completed_videos.all():
            course_progress.completed_videos.add(video)
        
        # Update course progress
        course_progress.update_progress()
        
        # Check if all videos are completed
        all_videos = Video.objects.filter(curriculum_day__course=course)
        total_videos = all_videos.count()
        completed_videos = UserVideoProgress.objects.filter(
            user=request.user,
            video__in=all_videos,
            is_completed=True
        ).count()
        
        all_videos_completed = (completed_videos == total_videos)
        
        # Check if course is fully completed (videos + quiz)
        course_completed = course_progress.check_completion()
        
        # Get certificate if generated
        certificate = None
        if course_completed:
            try:
                from .models import Certificate
                certificate = Certificate.objects.get(
                    user=request.user,
                    course=course
                )
            except Certificate.DoesNotExist:
                certificate = None
        
        # Check if course has quiz
        has_quiz = False
        try:
            has_quiz = hasattr(course, 'quiz') and course.quiz is not None
        except:
            has_quiz = False
        
        return JsonResponse({
            'success': True,
            'status': 'success',
            'progress_percentage': float(course_progress.progress_percentage),
            'all_videos_completed': all_videos_completed,
            'quiz_passed': course_progress.quiz_passed,
            'quiz_required': has_quiz,
            'course_completed': course_completed,
            'certificate_id': certificate.certificate_id if certificate else None,
            'message': 'Video marked as complete'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 'error',
            'error': str(e),
            'message': f'Error marking video complete: {str(e)}'
        }, status=400)
    
@login_required
def my_achievements(request):
    """Optimized version for better performance with large datasets"""
    from django.db.models import Prefetch, Count
    
    user = request.user
    
    # 1. Get certificates with optimized query
    certificates = Certificate.objects.filter(
        user=user
    ).select_related('course').order_by('-issue_date')
    
    # Debug: Print certificate count
    print(f"DEBUG: Total certificates for user {user.username}: {certificates.count()}")
    
    # 2. Get all courses the user has purchased
    purchased_course_ids = Purchase.objects.filter(
        user=user,
        payment_status='completed'
    ).values_list('course_id', flat=True)
    
    print(f"DEBUG: Purchased course IDs: {list(purchased_course_ids)}")
    
    purchased_courses = Course.objects.filter(
        id__in=purchased_course_ids
    ).prefetch_related(
        Prefetch(
            'curriculum_days__videos',
            queryset=Video.objects.only('id')
        )
    )
    
    # 3. Get course progress efficiently
    progress_queryset = CourseProgress.objects.filter(
        user=user,
        course__in=purchased_courses
    ).select_related('course').annotate(
        completed_videos_count=Count('completed_videos')
    )
    
    print(f"DEBUG: Progress queryset count: {progress_queryset.count()}")
    print(f"DEBUG: Quiz passed count: {progress_queryset.filter(quiz_passed=True).count()}")
    
    # 4. Calculate statistics
    total_courses = purchased_courses.count()
    total_certificates = certificates.count()
    
    # Count courses with certificates
    completed_courses = certificates.values('course').distinct().count()
    
    # Alternative: Count from progress
    completed_from_progress = progress_queryset.filter(is_completed=True).count()
    completed_courses = max(completed_courses, completed_from_progress)
    
    # Count total quizzes passed
    total_quiz_passed = progress_queryset.filter(quiz_passed=True).count()
    
    in_progress_courses = total_courses - completed_courses
    
    # 5. Build detailed progress list efficiently
    detailed_progress = []
    
    # Create a dictionary for quick lookup
    progress_dict = {p.course_id: p for p in progress_queryset}
    
    for course in purchased_courses:
        progress = progress_dict.get(course.id)
        
        if progress:
            # Get total videos count from prefetched data
            total_videos = sum(day.videos.count() for day in course.curriculum_days.all())
            
            # Calculate actual percentage
            if total_videos > 0:
                completed_videos = progress.completed_videos_count
                actual_percentage = (completed_videos / total_videos) * 100
            else:
                actual_percentage = progress.progress_percentage
            
            detailed_progress.append({
                'course': course,
                'progress_percentage': round(actual_percentage, 1),
                'is_completed': progress.is_completed,
                'quiz_passed': progress.quiz_passed,
                'completed_videos_count': progress.completed_videos_count,
                'total_videos': total_videos,
                'has_certificate': certificates.filter(course=course).exists(),
            })
    
    # 6. Sort progress
    detailed_progress.sort(
        key=lambda x: (
            not x['is_completed'],  # Completed first
            -x['progress_percentage']  # Higher percentage first
        )
    )
    
    print(f"DEBUG: Final counts - Certificates: {total_certificates}, Quizzes Passed: {total_quiz_passed}")
    
    context = {
        'certificates': certificates,
        'progress_data': detailed_progress,
        'completed_courses': completed_courses,
        'in_progress_courses': max(0, in_progress_courses),
        'total_courses': total_courses,
        'total_certificates': total_certificates,
        'total_quiz_passed': total_quiz_passed,
        'user': user,
    }
    
    return render(request, 'lms/achievements.html', context)
    
@login_required
def certificate_detail(request, certificate_id):
    """Display individual certificate"""
    certificate = get_object_or_404(
        Certificate, 
        certificate_id=certificate_id, 
        user=request.user
    )
    
    context = {
        'certificate': certificate,
    }
    return render(request, 'lms/certificate_detail.html', context)




# KEEP these imports
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from weasyprint import HTML  # ← ADD THIS
from .models import Certificate


@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id,
        user=request.user
    )

    html_string = render_to_string('lms/certificate_pdf.html', {
        'certificate': certificate,
        'request': request,
    })

    try:
        pdf_bytes = HTML(
            string=html_string,
            base_url=request.build_absolute_uri('/')
        ).write_pdf()

        # ✅ Fix
        student_name = certificate.user.get_full_name() or certificate.user.username
        safe_name = "".join(
            c if c.isalnum() or c == '_' else '_'
            for c in student_name.replace(' ', '_')
        )

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{safe_name}_Certificate.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)



from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Avg, Sum  # ← ADD THIS LINE
from django.contrib.auth.decorators import login_required

# For PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
import re

# Your models
from .models import Course, Video, CurriculumDay, Instructor, Tool

# ... rest of your imports ...


# Then add this function:
def download_brochure(request, slug):
    """Generate PDF brochure using ReportLab"""
    course = get_object_or_404(Course, slug=slug)
    
    # Create BytesIO buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=20,
        alignment=1,  # Center
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#065f46'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    # Title
    elements.append(Paragraph(course.title, title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Description
    if course.description:
        elements.append(Paragraph("Course Description", heading_style))
        # Remove HTML tags from description
        clean_desc = re.sub('<[^<]+?>', '', course.description)
        elements.append(Paragraph(clean_desc[:500], styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Course Details Table
    elements.append(Paragraph("Course Details", heading_style))
    details_data = [
        ['Duration', f"{course.duration_hours} Hours"],
        ['Original Price', f"₹{course.original_price}"],
        ['Discounted Price', f"₹{course.discounted_price}"],
        ['Language', course.languages or 'English'],
        ['Access Level', course.access_level or 'All Levels'],
        ['Total Learners', str(course.total_learners)],
    ]
    
    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d1fae5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Instructors
    instructors = course.instructors.all()
    if instructors:
        elements.append(Paragraph("Instructors", heading_style))
        instructor_names = ", ".join([inst.name for inst in instructors])
        elements.append(Paragraph(instructor_names, styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Curriculum
    elements.append(Paragraph("Course Curriculum", heading_style))
    
    curriculum_days = course.curriculum_days.all().prefetch_related('videos')
    for day in curriculum_days:
        # Day title
        day_title = f"<b>Day {day.day_number}: {day.title}</b>"
        elements.append(Paragraph(day_title, styles['Normal']))
        elements.append(Spacer(1, 0.05*inch))
        
        # Videos
        videos = day.videos.all()
        for video in videos:
            video_text = f"&nbsp;&nbsp;&nbsp;&nbsp;• {video.title} ({video.duration} min)"
            elements.append(Paragraph(video_text, styles['Normal']))
        
        elements.append(Spacer(1, 0.15*inch))
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_text = f"<i>For more information, visit our website or contact us.</i>"
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{course.slug}_brochure.pdf"'
    response.write(pdf)
    
    return response


from django.http import HttpResponse
import re

def fix_images(request):
    from lms.models import HeroSection, HomeAboutSection, Instructor, Course, HomeBanner, Testimonial
    
    results = []
    
    def fix_cloudinary_field(model, field_name):
        for obj in model.objects.all():
            val = str(getattr(obj, field_name))
            if not val or val == 'None':
                continue
            if 'res.cloudinary.com' in val:
                clean = re.sub(r'https://res\.cloudinary\.com/[^/]+/image/upload/(v\d+/)?', '', val)
                clean = re.sub(r'\.(jpg|jpeg|png|gif|webp)$', '', clean, flags=re.IGNORECASE)
                setattr(obj, field_name, clean)
                obj.save()
                results.append(f"{model.__name__} id={obj.id}: fixed -> {clean}")
    
    fix_cloudinary_field(HeroSection, 'hero_image')
    fix_cloudinary_field(HomeAboutSection, 'image')
    fix_cloudinary_field(Instructor, 'profile_image')
    fix_cloudinary_field(Course, 'thumbnail')
    fix_cloudinary_field(HomeBanner, 'image')
    fix_cloudinary_field(Testimonial, 'profile_image')
    
    return HttpResponse("<br>".join(results) if results else "Already fixed or nothing to fix!")