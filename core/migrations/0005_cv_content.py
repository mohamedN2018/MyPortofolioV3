"""
One-time content alignment with the latest CV (2026-11-06).

Non-destructive: updates names/bio/profiles, creates the CV's experience,
education, skills and project case studies, and DEACTIVATES (never deletes)
outdated rows. Reverse is a no-op; re-enable rows from the admin if needed.
"""
from django.db import migrations


def forwards(apps, schema_editor):
    from core.brand_content import apply_brand_content
    apply_brand_content(apps.get_model, log=lambda m: None)


class Migration(migrations.Migration):
    dependencies = [("core", "0004_brand_identity_and_gallery")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
