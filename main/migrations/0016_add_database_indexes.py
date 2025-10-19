# Generated migration for database performance improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_exam_model_end_time_alter_exam_model_id_and_more'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_question_professor ON main_question_db (professor_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_question_professor;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_question_type ON main_question_db (question_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_question_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_exam_professor ON main_exam_model (professor_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_exam_professor;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_exam_start_time ON main_exam_model (start_time);",
            reverse_sql="DROP INDEX IF EXISTS idx_exam_start_time;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_exam_end_time ON main_exam_model (end_time);",
            reverse_sql="DROP INDEX IF EXISTS idx_exam_end_time;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_reference_answer_question ON main_referenceanswer (question_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_reference_answer_question;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_question_paper_professor ON main_question_paper (professor_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_question_paper_professor;"
        ),
    ]
