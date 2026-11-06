"""
Restore live links for three CV projects (owner request, 2026-11-07).

Only fills `project_url` where it is empty; never deletes or overwrites other data.
"""
from django.db import migrations

LINKS = {
    "qshop-multi-vendor-marketplace": "https://qshop.deplois.net/",
    "walaee-loyalty-network": "https://walaee.deplois.net/",
    "qtech-pharmasyst": "https://qtechpharmasyst.deplois.net/",
}


def forwards(apps, schema_editor):
    Portfolio = apps.get_model("core", "Portfolio")
    for slug, url in LINKS.items():
        Portfolio.objects.filter(slug__in=[slug, f"{slug}-ar"], project_url="").update(project_url=url)


class Migration(migrations.Migration):
    dependencies = [("core", "0005_cv_content")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
