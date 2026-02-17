from django.core.management.base import BaseCommand
from django.db.models import Q
from lms.models import Video
import cloudinary.api
from datetime import timedelta


class Command(BaseCommand):
    help = 'Extract and update video durations from Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-extract duration even if already set',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('VIDEO DURATION EXTRACTION FROM CLOUDINARY'))
        self.stdout.write(self.style.WARNING('='*60 + '\n'))

        # Get videos to process
        if force:
            videos = Video.objects.filter(video_file__isnull=False)
            self.stdout.write(f"Processing ALL videos with files (--force): {videos.count()}")
        else:
            videos = Video.objects.filter(
                Q(video_file__isnull=False) & 
                (Q(duration__isnull=True) | Q(duration=timedelta(0)))
            )
            self.stdout.write(f"Processing videos WITHOUT duration: {videos.count()}")

        if not videos.exists():
            self.stdout.write(self.style.SUCCESS('\n✅ No videos need processing!'))
            return

        # Process each video
        success_count = 0
        failed_count = 0
        skipped_count = 0

        for i, video in enumerate(videos, 1):
            self.stdout.write(f"\n[{i}/{videos.count()}] Processing: {video.title}")
            self.stdout.write(f"    Course: {video.curriculum_day.course.title}")
            self.stdout.write(f"    Day: {video.curriculum_day.day_number}")

            try:
                # Get public_id
                public_id = None
                
                if hasattr(video.video_file, 'public_id'):
                    public_id = video.video_file.public_id
                    self.stdout.write(f"    📝 Public ID (attribute): {public_id}")
                else:
                    public_id = self._extract_public_id(str(video.video_file))
                    self.stdout.write(f"    📝 Public ID (extracted): {public_id}")

                if not public_id:
                    self.stdout.write(self.style.ERROR(f"    ❌ Could not extract public_id"))
                    failed_count += 1
                    continue

                # Query Cloudinary
                self.stdout.write(f"    🌐 Querying Cloudinary...")
                resource = cloudinary.api.resource(
                    public_id,
                    resource_type="video"
                )

                duration_seconds = resource.get('duration')
                
                if duration_seconds and duration_seconds > 0:
                    duration = timedelta(seconds=int(duration_seconds))
                    
                    # Update video
                    video.duration = duration
                    video.save(update_fields=['duration'])
                    
                    # Display result
                    h, remainder = divmod(int(duration_seconds), 3600)
                    m, s = divmod(remainder, 60)
                    
                    if h > 0:
                        time_str = f"{h}:{m:02d}:{s:02d}"
                    elif m > 0:
                        time_str = f"{m}:{s:02d}"
                    else:
                        time_str = f"{s}s"
                    
                    self.stdout.write(self.style.SUCCESS(f"    ✅ Duration: {time_str}"))
                    success_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f"    ⚠️ Duration is 0 or missing in Cloudinary"))
                    skipped_count += 1

            except cloudinary.api.NotFound:
                self.stdout.write(self.style.ERROR(f"    ❌ Video not found in Cloudinary"))
                failed_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    ❌ Error: {type(e).__name__}: {e}"))
                failed_count += 1

        # Summary
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('SUMMARY'))
        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(self.style.SUCCESS(f"✅ Success: {success_count}"))
        self.stdout.write(self.style.WARNING(f"⚠️  Skipped: {skipped_count}"))
        self.stdout.write(self.style.ERROR(f"❌ Failed:  {failed_count}"))
        self.stdout.write(self.style.WARNING('='*60 + '\n'))

    def _extract_public_id(self, video_str):
        """Extract public_id from Cloudinary URL"""
        try:
            if 'cloudinary.com' in video_str:
                parts = video_str.split('/')
                
                if 'upload' in parts:
                    upload_idx = parts.index('upload')
                    start_idx = upload_idx + 2  # Skip version
                    
                    path_parts = parts[start_idx:]
                    filename = path_parts[-1].rsplit('.', 1)[0]
                    folder = '/'.join(path_parts[:-1])
                    
                    if folder:
                        return f"{folder}/{filename}"
                    return filename
            
            return None
        except:
            return None