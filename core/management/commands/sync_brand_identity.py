"""
Re-apply the CV-based brand content (same logic as migration 0005).

    python manage.py sync_brand_identity            # dry run
    python manage.py sync_brand_identity --apply    # write

Non-destructive: outdated rows are deactivated, never deleted.
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import transaction

from core.brand_content import apply_brand_content


class Command(BaseCommand):
    help = "Align site content with the latest CV (core/brand_content.py)."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Write changes (default: dry run).")

    def handle(self, *args, **opts):
        dry = not opts["apply"]
        prefix = "[dry-run] " if dry else ""
        with transaction.atomic():
            apply_brand_content(apps.get_model, log=lambda m: self.stdout.write(prefix + m), dry_run=dry)
        self.stdout.write(self.style.SUCCESS("Dry run complete — re-run with --apply." if dry else "Done."))
