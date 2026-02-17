# lms/migrations/0016_fix_postgres_video_tools.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('lms', '0015_remove_video_duration'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS "lms_video_tools_needed" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "video_id" bigint NOT NULL,
                "tool_id" bigint NOT NULL,
                UNIQUE ("video_id", "tool_id")
            );
            
            ALTER TABLE "lms_video_tools_needed" 
            ADD CONSTRAINT "lms_video_tools_needed_video_id_fkey" 
            FOREIGN KEY ("video_id") 
            REFERENCES "lms_video" ("id") 
            ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
            
            ALTER TABLE "lms_video_tools_needed" 
            ADD CONSTRAINT "lms_video_tools_needed_tool_id_fkey" 
            FOREIGN KEY ("tool_id") 
            REFERENCES "lms_tool" ("id") 
            ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
            
            CREATE INDEX IF NOT EXISTS "lms_video_tools_needed_video_id" 
            ON "lms_video_tools_needed" ("video_id");
            
            CREATE INDEX IF NOT EXISTS "lms_video_tools_needed_tool_id" 
            ON "lms_video_tools_needed" ("tool_id");
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS "lms_video_tools_needed" CASCADE;
            """
        ),
    ]