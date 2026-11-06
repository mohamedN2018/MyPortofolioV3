from cryptography.fernet import Fernet
from django.conf import settings
from django.core.management.base import BaseCommand

from hub import crypto
from hub.models import ConnectedAccount, IntegrationToken, OwnerMFA


class Command(BaseCommand):
    help = "Security checks for the AI Hub; --new-key prints a fresh Fernet key; --rotate re-encrypts with the newest key."

    def add_arguments(self, parser):
        parser.add_argument("--new-key", action="store_true")
        parser.add_argument("--rotate", action="store_true")

    def handle(self, *args, **opts):
        if opts["new_key"]:
            self.stdout.write(Fernet.generate_key().decode())
            return
        if opts["rotate"]:
            n = 0
            for t in IntegrationToken.objects.exclude(ciphertext=""):
                t.ciphertext = crypto.rotate(t.ciphertext)
                t.save(update_fields=["ciphertext"])
                n += 1
            for m in OwnerMFA.objects.all():
                m.secret_enc = crypto.rotate(m.secret_enc)
                m.save(update_fields=["secret_enc"])
                n += 1
            self.stdout.write(f"re-encrypted {n} secrets")
            return
        problems = []
        if not crypto.explicit_key_configured():
            problems.append("HUB_ENCRYPTION_KEYS not set (dev fallback key derived from SECRET_KEY in use)")
        if settings.DEBUG:
            problems.append("DEBUG is on")
        media, private = str(settings.MEDIA_ROOT), str(settings.HUB_PRIVATE_ROOT)
        if private.startswith(media):
            problems.append("HUB_PRIVATE_ROOT is inside MEDIA_ROOT (would be publicly served)")
        if not OwnerMFA.objects.filter(enabled=True).exists():
            problems.append("Two-factor authentication is not enabled for the owner")
        self.stdout.write(f"accounts: {ConnectedAccount.objects.count()}, tokens: {IntegrationToken.objects.filter(revoked_at__isnull=True).count()}")
        for p in problems:
            self.stdout.write(self.style.WARNING(f"WARN: {p}"))
        if not problems:
            self.stdout.write(self.style.SUCCESS("All hub security checks passed."))
