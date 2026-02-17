from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.text import Truncator
from .models import (
    User,
    HeroSection,
    FeatureSection,
    FeatureItem,
    HomeAboutSection,
    Category,
    CourseCategory,
    Instructor,
    Course,
    CourseTool,
    CurriculumDay,
    Video,
    Lesson,
    CourseReview,
    CourseEnrollment,
    Payment,
    Purchase,
    UserVideoProgress,
)


# ============================
# CUSTOM USER ADMIN
# ============================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'username', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'username')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password1',
                'password2',
                'is_staff',
                'is_superuser',
            ),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')


# ============================
# HERO SECTION ADMIN
# ============================
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('title_primary', 'is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('title_primary', 'title_secondary')


# ============================
# FEATURE SECTION ADMIN
# ============================
class FeatureItemInline(admin.TabularInline):
    model = FeatureItem
    extra = 1


@admin.register(FeatureSection)
class FeatureSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_editable = ('is_active',)
    inlines = [FeatureItemInline]


# ============================
# HOME ABOUT SECTION ADMIN
# ============================
@admin.register(HomeAboutSection)
class HomeAboutSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_preview_list', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('is_active', 'order')
    search_fields = ('title', 'subtitle', 'team_description')
    
    fieldsets = (
        ('Main Content', {
            'fields': ('title', 'subtitle', 'description', 'image', 'image_preview')
        }),
        ('Team Section', {
            'fields': ('team_title', 'team_description')
        }),
        ('Button Settings', {
            'fields': ('button_text', 'button_link')
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )
    
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" style="border-radius: 5px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    def image_preview_list(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview_list.short_description = 'Image'


# ============================
# CATEGORY ADMIN
# ============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order',)


# ============================
# COURSE CATEGORY ADMIN
# ============================
@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'is_active', 'order', 'course_count']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Number of Courses'


# ============================
# INSTRUCTOR ADMIN
# ============================
@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation','bio']
    search_fields = ['name']


# ============================
# COURSE INLINES
# ============================
class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ['title', 'description', 'duration', 'video_url', 'order', 'is_free']


class CurriculumDayInline(admin.TabularInline):
    model = CurriculumDay
    extra = 1
    fields = ['day_number', 'title', 'is_free', 'order']
    show_change_link = True



class CourseToolInline(admin.TabularInline):
    model = CourseTool
    extra = 1
    fields = ['tool_name']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['module_title', 'title', 'duration', 'is_preview', 'order']
    ordering = ['order']


class CourseReviewInline(admin.TabularInline):
    model = CourseReview
    extra = 0
    readonly_fields = ['user', 'rating', 'comment', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False



from django.contrib import admin
from .models import Tool

@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_required', 'order', 'created_at']
    list_filter = ['category', 'is_required']
    search_fields = ['name', 'description']
    list_editable = ['order', 'is_required']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'is_required', 'order')
        }),
        ('Icon', {
            'fields': ('icon_class', 'icon_image'),
            'description': 'Choose either Font Awesome class OR upload custom image'
        }),
        ('Links', {
            'fields': ('download_url',)
        }),
    )

# ============================
# COURSE ADMIN
# ============================
from django.contrib import admin
from django.utils.html import format_html
from .models import Course


from django.contrib import admin
from django.utils.html import format_html
from .models import Course

from django.contrib import admin
from django.utils.html import format_html
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # =========================
    # LIST PAGE
    # =========================
    list_display = (
        'title',
        'category',
        'level',
        'display_skills_icons',  # NEW: Skills icons
        'display_tools_icons',   # NEW: Tools icons
        'original_price',
        'discounted_price',
        'is_free',
        'is_active',
        'is_featured',
        'created_at',
        'total_learners',   # New field
        'payment_type',
    )

    list_filter = (
        'is_active',
        'is_featured',
        'is_free',
        'level',
        'category',
        'created_at',
    )

    search_fields = (
        'title',
        'short_description',
        'tagline',
        'skills',
        'tools_learned',
    )

    list_editable = (
        'is_active',
        'is_featured',
        'discounted_price',
    )
    
    inlines = [CurriculumDayInline]

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    # =========================
    # SLUG AUTO GENERATION
    # =========================
    prepopulated_fields = {
        'slug': ('title',)
    }

    filter_horizontal = ['tools']

    # =========================
    # FORM LAYOUT
    # =========================
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'slug',
                'tagline',
                'short_description',
                'description',
            )
        }),

        ('Category & Instructors', {
            'fields': (
                'category',
                'instructors',
            )
        }),

        ('Pricing', {
            'fields': (
                'original_price',
                'discounted_price',
                'is_free',
            )
        }),

        ('Course Details', {
            'fields': (
                'level',
                'duration_hours',
                'languages',
                'access_level',
            )
        }),

        ('Course Content', {
            'fields': (
                'learning_outcomes',
                'prerequisites',
                'skills',
                'skills_icons_preview',  # NEW: Skills icons preview
                'tools_learned',
                'tools_icons_preview',   # NEW: Tools icons preview
                'certification_details',
            )
        }),

        ('Statistics', {
            'fields': (
                'total_videos',
                'total_projects',
                'total_resources',
            )
        }),

        ('Media', {
            'fields': (
                'thumbnail',
                'preview_video_url',
            )
        }),

        ('Status', {
            'fields': (
                'is_active',
                'is_featured',
            )
        }),

        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'skills_icons_preview',  # NEW
        'tools_icons_preview',   # NEW
    )

    # =========================
    # MANY-TO-MANY UX
    # =========================
    filter_horizontal = ('instructors',)

    # =========================
    # ADMIN ACTIONS
    # =========================
    actions = [
        'mark_active',
        'mark_inactive',
        'mark_featured',
    ]

    @admin.action(description="Mark selected courses as Active")
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Mark selected courses as Inactive")
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Mark selected courses as Featured")
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)

    # =========================
    # VISUAL POLISH
    # =========================
    save_on_top = True

    # =========================
    # SIMPLE METHODS WITHOUT format_html ERRORS
    # =========================
    
    def display_skills_icons(self, obj):
        """Simple text display for skills"""
        skills = obj.get_skills_list()[:3]
        if not skills:
            return '-'
        return ', '.join(skills)
    display_skills_icons.short_description = 'Skills'

    def display_tools_icons(self, obj):
        """Simple text display for tools"""
        tools = obj.get_tools_list()[:3]
        if not tools:
            return '-'
        return ', '.join(tools)
    display_tools_icons.short_description = 'Tools'

    def skills_icons_preview(self, obj):
        """Simple text preview without HTML"""
        if not obj.pk:
            return 'Save the course first to see skills'
        
        skills = obj.get_skills_list()
        if not skills:
            return 'No skills entered. Add comma-separated skills like: Python, Django, HTML, CSS'
        
        # Return plain text instead of HTML
        return f"Skills ({len(skills)}): {', '.join(skills)}"
    skills_icons_preview.short_description = 'Skills Preview'

    def tools_icons_preview(self, obj):
        """Simple text preview without HTML"""
        if not obj.pk:
            return 'Save the course first to see tools'
        
        tools = obj.get_tools_list()
        if not tools:
            return 'No tools entered. Add comma-separated tools like: VSCode, GitHub, Docker, Figma'
        
        # Return plain text instead of HTML
        return f"Tools ({len(tools)}): {', '.join(tools)}"
    tools_icons_preview.short_description = 'Tools Preview'

    # =========================
    # ADD FONT AWESOME CSS (SINGLE COPY)
    # =========================
    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',)
        }





from django.contrib import admin
from django.utils.html import format_html
from datetime import timedelta

from .models import (
    Video,
    CurriculumDay,
    Course,
)

# =====================================================
# VIDEO INLINE (Inside Curriculum Day)
# =====================================================
from django.contrib import admin
from datetime import timedelta
from .models import CurriculumDay, Video, Course

# -----------------------------
# Video Inline for CurriculumDay
# -----------------------------
# class VideoInline(admin.TabularInline):
#     model = Video
#     extra = 1
#     fields = [
#         'title',
#         'video_url',
#         'video_file',
#         'thumbnail',
#         'order',
#         'is_free',
#         'show_duration',
#     ]
#     readonly_fields = ['show_duration']

#     def show_duration(self, obj):
#         if obj.duration:
#             return obj.duration_display
#         return "N/A"
#     show_duration.short_description = 'Duration'


# # -----------------------------
# # CurriculumDay Admin
# # -----------------------------
# @admin.register(CurriculumDay)
# class CurriculumDayAdmin(admin.ModelAdmin):
#     list_display = [
#         'get_course_title',
#         'day_number',
#         'title',
#         'is_free',
#         'order',
#         'video_count',
#         'total_duration_display',
#     ]
#     list_filter = [
#         'course',  # This allows filtering by course
#         'is_free',
#     ]
#     search_fields = [
#         'course__title',
#         'title',
#     ]
#     ordering = [
#         'course',  # Groups by course first
#         'order',
#         'day_number',
#     ]
    
#     # ADD THIS to make it easier to filter
#     list_per_page = 20  # Show 20 per page
    
#     # ADD THIS to show course filter prominently
#     list_select_related = ['course']  # Optimize queries
    
#     inlines = [VideoInline]

#     # -----------------------------
#     # Helper methods
#     # -----------------------------
#     def get_course_title(self, obj):
#         return obj.course.title
#     get_course_title.short_description = 'Course'
#     get_course_title.admin_order_field = 'course'

#     def video_count(self, obj):
#         return obj.videos.count()
#     video_count.short_description = 'Videos'

#     def total_duration_display(self, obj):
#         """Total duration of all videos in this day"""
#         total = timedelta()

#         for video in obj.videos.all():
#             if video.duration:
#                 total += video.duration

#         total_seconds = int(total.total_seconds())
#         hours, remainder = divmod(total_seconds, 3600)
#         minutes, seconds = divmod(remainder, 60)

#         if hours > 0:
#             return f"{hours}h {minutes}m"
#         elif minutes > 0:
#             return f"{minutes}m"
#         elif seconds > 0:
#             return f"{seconds}s"
#         return "0m"

#     total_duration_display.short_description = 'Total Duration'



# =====================================================
# VIDEO ADMIN
# =====================================================

# Add this to your admin.py for Video model

from django.contrib import admin
from django.utils.html import format_html
from .models import Video
from datetime import timedelta


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'get_course',
        'get_day',
        'show_duration',
        'has_cloudinary_file',
        'order',
        'is_free',
    ]

    list_filter = [
        'curriculum_day__course',
        'curriculum_day',
        'is_free',
    ]

    search_fields = [
        'title',
        'curriculum_day__title',
        'curriculum_day__course__title',
    ]

    ordering = [
        'curriculum_day__course',
        'curriculum_day__order',
        'order',
    ]

    readonly_fields = [
        'show_duration',
        'show_file_size',
        'show_public_id',
    ]
    
    # ✅ NEW: Admin action to refresh durations
    actions = ['refresh_duration_from_cloudinary']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'curriculum_day',
                'title',
                'description',
                'order',
                'is_free',
            )
        }),
        ('Video Sources', {
            'fields': (
                'video_url',
                'video_file',
                'thumbnail',
            ),
            'description': 'Add YouTube/Vimeo URL OR upload a video file to Cloudinary.',
        }),
        ('Tools', {
            'fields': ('tools_needed',),
        }),
        ('Auto Generated Info', {
            'fields': (
                'show_duration',
                'show_file_size',
                'show_public_id',
            ),
            'classes': ('collapse',),
        }),
    )

    # -----------------------------
    # Custom Display Methods
    # -----------------------------
    def get_course(self, obj):
        return obj.curriculum_day.course.title
    get_course.short_description = 'Course'
    get_course.admin_order_field = 'curriculum_day__course'

    def get_day(self, obj):
        return f"Day {obj.curriculum_day.day_number}"
    get_day.short_description = 'Day'
    get_day.admin_order_field = 'curriculum_day__day_number'

    def show_duration(self, obj):
        """Display duration with color coding"""
        if obj.duration:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ {}</span>',
                obj.duration_display
            )
        elif obj.video_file:
            return format_html(
                '<span style="color: orange;">⚠️ Click refresh action</span>'
            )
        return format_html('<span style="color: gray;">-</span>')
    show_duration.short_description = 'Duration'

    def show_file_size(self, obj):
        if obj.video_file and obj.file_size > 0:
            return f"{obj.file_size} MB"
        return "N/A"
    show_file_size.short_description = 'File Size'

    def show_public_id(self, obj):
        """Show Cloudinary public_id for debugging"""
        if obj.video_file:
            if hasattr(obj.video_file, 'public_id'):
                return obj.video_file.public_id
            return obj._extract_public_id_from_url() or "Could not extract"
        return "No file"
    show_public_id.short_description = 'Cloudinary Public ID'

    def has_cloudinary_file(self, obj):
        """Show if video file exists"""
        return bool(obj.video_file)
    has_cloudinary_file.boolean = True
    has_cloudinary_file.short_description = 'Has File'

    # -----------------------------
    # ✅ ADMIN ACTION: Refresh Duration
    # -----------------------------
    @admin.action(description="🔄 Refresh duration from Cloudinary")
    def refresh_duration_from_cloudinary(self, request, queryset):
        """
        Admin action to refresh duration for selected videos
        """
        updated = 0
        failed = 0
        no_file = 0
        
        for video in queryset:
            if not video.video_file:
                no_file += 1
                continue
            
            # Attempt to refresh
            if video.refresh_duration():
                updated += 1
            else:
                failed += 1
        
        # Show results
        messages = []
        if updated > 0:
            messages.append(f"✅ Successfully updated {updated} video(s)")
        if failed > 0:
            messages.append(f"❌ Failed to update {failed} video(s)")
        if no_file > 0:
            messages.append(f"⚠️ {no_file} video(s) had no file")
        
        self.message_user(
            request,
            " | ".join(messages)
        )


# =====================================================
# CURRICULUM DAY ADMIN (Optional Enhancement)
# =====================================================
from .models import CurriculumDay

class VideoInline(admin.TabularInline):
    model = Video
    extra = 0
    fields = [
        'title',
        'video_url',
        'video_file',
        'duration_display_inline',
        'order',
        'is_free',
    ]
    readonly_fields = ['duration_display_inline']

    def save_model(self, request, obj, form, change):
        # Force duration extraction when video_file changes
        if obj.video_file:
            old_file = None
            if obj.pk:
                try:
                    old = Video.objects.get(pk=obj.pk)
                    old_file = str(old.video_file)
                except Video.DoesNotExist:
                    pass

            # If video changed or duration is missing, reset duration
            if str(obj.video_file) != old_file or not obj.duration:
                obj.duration = None  # Force re-extraction in save()

        obj.save()

    def duration_display_inline(self, obj):
        if obj.duration:
            return obj.duration_display
        elif obj.video_file:
            return "⚠️ Refresh needed"
        return "-"
    duration_display_inline.short_description = 'Duration'


@admin.register(CurriculumDay)
class CurriculumDayAdmin(admin.ModelAdmin):
    list_display = [
        'get_course_title',
        'day_number',
        'title',
        'is_free',
        'order',
        'video_count',
        'total_duration_display',
    ]
    list_filter = ['course', 'is_free']
    search_fields = ['course__title', 'title']
    ordering = ['course', 'order', 'day_number']
    inlines = [VideoInline]

    def get_course_title(self, obj):
        return obj.course.title
    get_course_title.short_description = 'Course'

    def video_count(self, obj):
        return obj.videos.count()
    video_count.short_description = 'Videos'

    def total_duration_display(self, obj):
        """Calculate total duration of all videos in this day"""
        total = timedelta()
        
        for video in obj.videos.all():
            if video.duration:
                total += video.duration
        
        if total.total_seconds() == 0:
            return "-"
        
        total_seconds = int(total.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    
    total_duration_display.short_description = 'Total Duration'



# =====================================================
# COURSE ADMIN (OPTIONAL INLINE)
# =====================================================
from django.contrib import admin
from .models import Course, CurriculumDay


class CurriculumDayInline(admin.TabularInline):
    model = CurriculumDay
    extra = 0
    ordering = ('order', 'day_number')
    fields = (
        'day_number',
        'title',
        'is_free',
        'order',
    )




# ============================
# LESSON ADMIN (Legacy)
# ============================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'module_title', 'duration', 'is_preview', 'order']
    list_editable = ['order', 'is_preview']
    list_filter = ['course', 'is_preview', 'module_title']
    search_fields = ['title', 'content', 'module_title']
    list_select_related = ['course']
    
    fieldsets = (
        ('Lesson Information', {
            'fields': (
                'course',
                'module_title',
                'title',
                'content',
            )
        }),
        
        ('Media & Duration', {
            'fields': (
                'video_url',
                'duration',
            )
        }),
        
        ('Settings', {
            'fields': (
                'is_preview',
                'order',
            )
        }),
    )


# ============================
# PURCHASE ADMIN (New System)
# ============================
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount_paid', 'payment_status', 'purchased_at']
    list_filter = ['payment_status', 'purchased_at', 'course']
    search_fields = ['user__username', 'user__email', 'full_name', 'email', 'transaction_id']
    readonly_fields = ['purchased_at']
    date_hierarchy = 'purchased_at'
    
    fieldsets = (
        ('Purchase Information', {
            'fields': ('user', 'course', 'amount_paid', 'payment_status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'purchased_at')
        }),
        ('User Details', {
            'fields': ('full_name', 'email')
        }),
    )




# ============================
# COURSE REVIEW ADMIN
# ============================
from django.contrib import admin
from .models import CourseReview

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'course']
    search_fields = ['name', 'review']
    readonly_fields = ['created_at', 'updated_at']


# ============================
# COURSE ENROLLMENT ADMIN
# ============================
@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrollment_type', 'is_paid', 'enrolled_at', 'expires_at', 'course_link']
    list_filter = ['enrollment_type', 'is_paid', 'enrolled_at']
    search_fields = ['user__email', 'user__username', 'course__title', 'transaction_id']
    readonly_fields = ['enrolled_at']
    list_select_related = ['user', 'course']
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('user', 'course', 'enrollment_type', 'is_paid')
        }),
        ('Dates', {
            'fields': ('enrolled_at', 'expires_at')
        }),
        ('Transaction', {
            'fields': ('transaction_id',)
        }),
    )
    
    def course_link(self, obj):
        url = reverse('admin:lms_course_change', args=[obj.course.id])
        return format_html('<a href="{}">{}</a>', url, obj.course.title)
    course_link.short_description = 'Course (Admin)'
    
    def has_add_permission(self, request):
        return False


# ============================
# PAYMENT ADMIN (Razorpay)
# ============================
# lms/admin.py
from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
    
    list_display = ['user', 'course', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['user__email', 'razorpay_order_id', 'razorpay_payment_id']
    
    fieldsets = (
        ('User & Course', {
            'fields': ('user', 'course')
        }),
        ('Razorpay Details', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature')
        }),
        ('Payment Info', {
            'fields': ('amount', 'currency', 'status', 'payment_method', 'payment_date')
        }),
        ('Billing Info', {
            'fields': (
                'billing_first_name', 'billing_last_name',
                'billing_email', 'billing_phone',
                'billing_address', 'billing_city',
                'billing_state', 'billing_zip_code',
                'billing_country'
            )
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

# ============================
# USER VIDEO PROGRESS ADMIN (Legacy)
# ============================
from django.contrib import admin
from .models import UserVideoProgress

@admin.register(UserVideoProgress)
class UserVideoProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'progress_percentage', 'is_completed', 'watched_duration_display', 'last_watched')
    list_filter = ('is_completed', 'last_watched')
    search_fields = ('user__email', 'user__username', 'video__title')
    readonly_fields = ('last_watched',)
    list_select_related = ['user', 'video', 'video__curriculum_day']
    
    # Add this method for progress_percentage
    def progress_percentage(self, obj):
        """
        Calculate and display progress as percentage
        """
        # Check if video has duration field
        if obj.video and hasattr(obj.video, 'duration'):
            if obj.video.duration > 0:
                # Assuming watched_duration is in seconds
                percentage = (obj.watched_duration / obj.video.duration) * 100
                return f"{percentage:.1f}%"
        return "0%"
    
    progress_percentage.short_description = 'Progress %'
    
    def watched_duration_display(self, obj):
        minutes = obj.watched_duration // 60
        seconds = obj.watched_duration % 60
        return f"{minutes}m {seconds}s"
    watched_duration_display.short_description = 'Watched Duration'


# ============================
# ADMIN SITE CUSTOMIZATION
# ============================
admin.site.site_header = "E-Learning Platform Admin"
admin.site.site_title = "E-Learning Admin Portal"
admin.site.index_title = "Welcome to E-Learning Platform Administration"


# homepage
from django.contrib import admin
from .models import HomeBanner

@admin.register(HomeBanner)
class HomeBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'highlight_text', 'subtitle', 'button_text', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    search_fields = ['title', 'subtitle', 'highlight_text']


from django.contrib import admin
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'role')

    from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('question',)

from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('name', 'email')


# quizz
# Add to lms/admin.py

from django.contrib import admin
from .models import (
    Quiz, Question, Answer, QuizAttempt, 
    QuizResponse, CourseProgress, Certificate
)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['answer_text', 'is_correct', 'order']

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['question_text', 'question_type', 'points', 'order', 'explanation']
    show_change_link = True

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'passing_score', 'time_limit', 'max_attempts', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'course__title']
    inlines = [QuestionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('course', 'title', 'description', 'is_active')
        }),
        ('Quiz Settings', {
            'fields': ('passing_score', 'time_limit', 'max_attempts', 'show_correct_answers')
        }),
    )

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'quiz', 'question_type', 'points', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text']
    inlines = [AnswerInline]
    list_editable = ['order']
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + "..." if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text_short', 'question', 'is_correct', 'order']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['answer_text']
    list_editable = ['is_correct', 'order']
    
    def answer_text_short(self, obj):
        return obj.answer_text[:50] + "..." if len(obj.answer_text) > 50 else obj.answer_text
    answer_text_short.short_description = 'Answer'

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'passed', 'started_at', 'completed_at', 'time_taken_display')
    list_filter = ('passed', 'started_at', 'quiz__course')
    search_fields = ('user__email', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at', 'score', 'passed', 'time_taken')
    date_hierarchy = 'started_at'
    inlines = []  # Can add QuizResponseInline if needed
    
    def time_taken_display(self, obj):
        if obj.time_taken:
            minutes = obj.time_taken // 60
            seconds = obj.time_taken % 60
            return f"{minutes}m {seconds}s"
        return "-"
    time_taken_display.short_description = 'Time Taken'
    
    def has_add_permission(self, request):
        return False  # Quiz attempts should be created by users

@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct']
    list_filter = ['attempt__quiz']
    readonly_fields = ['is_correct']

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'progress_percentage', 'quiz_passed', 'is_completed', 'completed_at', 'has_valid_quiz_attempt')
    list_filter = ('quiz_passed', 'is_completed', 'course')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('progress_percentage', 'completed_at', 'last_quiz_attempt_id', 'completion_details')
    actions = ['reset_quiz_status', 'recalculate_progress']
    
    def has_valid_quiz_attempt(self, obj):
        return bool(obj.last_quiz_attempt_id)
    has_valid_quiz_attempt.boolean = True
    has_valid_quiz_attempt.short_description = 'Valid Quiz Attempt'
    
    def completion_details(self, obj):
        requirements = obj.get_completion_requirements()
        return format_html("""
            <strong>Videos:</strong> {} / {} ({:.1f}%)<br>
            <strong>Quiz Passed:</strong> {}<br>
            <strong>Requirements Met:</strong> {}<br>
            <strong>Valid Quiz Attempt:</strong> {}
        """,
        requirements['completed_videos'],
        requirements['total_videos'],
        requirements['videos_percentage'],
        "✅ Yes" if requirements['quiz_actually_passed'] else "❌ No",
        "✅ All" if requirements['requirements_met']['all'] else "❌ Not yet",
        "✅ Yes" if obj.last_quiz_attempt_id else "❌ No")
    completion_details.short_description = 'Completion Status'
    
    @admin.action(description="Reset quiz status for selected")
    def reset_quiz_status(self, request, queryset):
        updated = 0
        for progress in queryset:
            progress.reset_quiz_status()
            updated += 1
        self.message_user(request, f"Reset quiz status for {updated} records.")
    
    @admin.action(description="Recalculate progress for selected")
    def recalculate_progress(self, request, queryset):
        updated = 0
        for progress in queryset:
            progress.update_progress()
            progress.check_completion()
            updated += 1
        self.message_user(request, f"Recalculated progress for {updated} records.")

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'certificate_id', 'quiz_score', 'issue_date']
    list_filter = ['issue_date']
    search_fields = ['user__email', 'course__title', 'certificate_id']
    readonly_fields = ['certificate_id', 'issue_date', 'quiz_score']


