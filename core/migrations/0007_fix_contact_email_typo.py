"""Fix a typo in the production contact e-mail ("@g.com" -> "@gmail.com"), as written in the owner's CV."""
from django.db import migrations


def forwards(apps, schema_editor):
    SiteSetting = apps.get_model("core", "SiteSetting")
    for s in SiteSetting.objects.filter(contact_email__iendswith="@g.com"):
        if s.contact_email.lower() == "mohamednabilpro2024@g.com":
            s.contact_email = "MohaMedNabiLpro2024@gmail.com"
            s.save(update_fields=["contact_email"])


class Migration(migrations.Migration):
    dependencies = [("core", "0006_restore_project_links")]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
