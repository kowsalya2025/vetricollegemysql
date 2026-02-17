import os
import django
import cloudinary.uploader

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lms_project.settings")
django.setup()

from lms.models import (
    HeroSection,
    HomeAboutSection,
    Category,
    Instructor,
    Tool,
    Course,
    HomeBanner,
    Testimonial,
    CourseReview,
    Video
)

def upload_image_to_cloudinary(local_path, folder="django_media_migration"):
    if not local_path:
        return None
    if not os.path.exists(local_path):
        print(f"  ⚠️  File does not exist: {local_path}")
        return None
    try:
        result = cloudinary.uploader.upload(
            local_path,
            folder=folder,
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"  ❌ Error uploading {local_path}: {e}")
        return None

MODEL_FIELDS = [
    (HeroSection, ["hero_image"]),
    (HomeAboutSection, ["image"]),
    (Category, ["icon"]),
    (Instructor, ["profile_image"]),
    (Tool, ["icon_image"]),
    (Course, ["thumbnail"]),
    (HomeBanner, ["image"]),
    (Testimonial, ["profile_image"]),
    (CourseReview, ["photo"]),
    (Video, ["thumbnail"]),
]

MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')

for model, fields in MODEL_FIELDS:
    print(f"\n📦 Processing {model.__name__}...")
    instances = model.objects.all()

    for obj in instances:
        updated = False

        for field_name in fields:
            field_value = getattr(obj, field_name)

            # Skip if empty
            if not field_value:
                continue

            field_str = str(field_value)

            # ✅ Skip if already a Cloudinary URL
            if field_str.startswith("https://res.cloudinary.com"):
                print(f"  ✅ Already on Cloudinary: {field_name} for {obj}")
                continue

            # Build local file path from MEDIA_ROOT
            local_path = os.path.join(MEDIA_ROOT, field_str)

            if not os.path.exists(local_path):
                print(f"  ⚠️  Local file not found: {local_path}")
                continue

            # Upload to Cloudinary
            print(f"  ⬆️  Uploading {field_name} for {obj}...")
            url = upload_image_to_cloudinary(local_path)

            if url:
                # ✅ Correct way for CloudinaryField — setattr directly
                setattr(obj, field_name, url)
                updated = True
                print(f"  ✅ Uploaded -> {url}")

        if updated:
            obj.save()
            print(f"  💾 Saved: {obj}")

print("\n🎉 Migration complete!")
