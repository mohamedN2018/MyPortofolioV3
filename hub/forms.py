from django import forms
from django.core.exceptions import ValidationError

from .models import CVDocument, JobPreference, PrivateFact

MAX_UPLOAD = 5 * 1024 * 1024
MAGIC = {b"%PDF-": ".pdf", b"PK\x03\x04": ".docx"}


def _csv_list(value):
    return [v.strip() for v in (value or "").split(",") if v.strip()][:40]


class FactForm(forms.ModelForm):
    class Meta:
        model = PrivateFact
        fields = ["section", "key", "value_en", "value_ar", "source", "verified_at", "status", "visibility", "sensitive"]
        widgets = {"verified_at": forms.DateInput(attrs={"type": "date"}),
                   "value_en": forms.Textarea(attrs={"rows": 3}), "value_ar": forms.Textarea(attrs={"rows": 3, "dir": "rtl"})}


class DocumentForm(forms.ModelForm):
    class Meta:
        model = CVDocument
        fields = ["title", "kind", "market", "language", "file", "text_content", "source", "verified_at", "status", "is_default"]
        widgets = {"verified_at": forms.DateInput(attrs={"type": "date"}), "text_content": forms.Textarea(attrs={"rows": 6})}

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f or not hasattr(f, "read"):
            return f
        if f.size > MAX_UPLOAD:
            raise ValidationError("Max 5 MB.")
        head = f.read(8)
        f.seek(0)
        ext = next((e for m, e in MAGIC.items() if head.startswith(m)), None)
        if not ext or not f.name.lower().endswith(ext):
            raise ValidationError("Only real PDF or DOCX files are accepted.")
        return f

    def clean(self):
        data = super().clean()
        if data.get("kind") == "cv" and not data.get("file") and not self.instance.file:
            raise ValidationError("A CV needs a file.")
        return data


class PreferenceForm(forms.ModelForm):
    roles_csv = forms.CharField(label="Roles", required=False, help_text="Comma separated")
    locations_csv = forms.CharField(label="Locations", required=False)
    required_csv = forms.CharField(label="Required technologies", required=False)
    excluded_csv = forms.CharField(label="Excluded technologies", required=False)
    work_modes = forms.MultipleChoiceField(choices=[("remote", "Remote"), ("hybrid", "Hybrid"), ("onsite", "On-site")],
                                           required=False, widget=forms.CheckboxSelectMultiple)
    seniority = forms.MultipleChoiceField(choices=[("junior", "Junior"), ("mid", "Mid"), ("senior", "Senior")],
                                          required=False, widget=forms.CheckboxSelectMultiple)
    employment_types = forms.MultipleChoiceField(choices=[("full_time", "Full-time"), ("contract", "Contract"), ("part_time", "Part-time")],
                                                 required=False, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = JobPreference
        fields = ["salary_min", "salary_max", "salary_currency", "needs_sponsorship"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        i = self.instance
        if i.pk:
            self.initial.update(roles_csv=", ".join(i.roles), locations_csv=", ".join(i.locations),
                                required_csv=", ".join(i.required_tech), excluded_csv=", ".join(i.excluded_tech),
                                work_modes=i.work_modes, seniority=i.seniority, employment_types=i.employment_types)

    def save(self, commit=True):
        i = super().save(commit=False)
        d = self.cleaned_data
        i.roles, i.locations = _csv_list(d["roles_csv"]), _csv_list(d["locations_csv"])
        i.required_tech, i.excluded_tech = _csv_list(d["required_csv"]), _csv_list(d["excluded_csv"])
        i.work_modes, i.seniority, i.employment_types = d["work_modes"], d["seniority"], d["employment_types"]
        if commit:
            i.save()
        return i


class JobForm(forms.Form):
    url = forms.URLField(max_length=600, help_text="Official job page (https)")
    title = forms.CharField(max_length=200)
    company = forms.CharField(max_length=160)
    location = forms.CharField(max_length=160, required=False)
    market = forms.ChoiceField(choices=[("", "—"), ("egypt", "Egypt"), ("ksa", "Saudi Arabia"), ("uae", "UAE"), ("other", "Other")], required=False)
    work_mode = forms.ChoiceField(choices=[("unknown", "Not stated"), ("remote", "Remote"), ("hybrid", "Hybrid"), ("onsite", "On-site")])
    min_years = forms.IntegerField(min_value=0, max_value=40, required=False)
    salary_text = forms.CharField(max_length=120, required=False, help_text="Only if the posting states it")
    language_requirements = forms.CharField(max_length=200, required=False)
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": 8}), required=False, max_length=20000)

    def clean_url(self):
        url = self.cleaned_data["url"]
        if not url.startswith("https://"):
            raise ValidationError("Use the https:// link of the official posting.")
        return url


class AccountForm(forms.Form):
    method = forms.ChoiceField()
    label = forms.CharField(max_length=120, required=False, help_text="Company name or a label you recognise")
    account_identifier = forms.CharField(max_length=200, required=False,
                                         help_text="Username/email, or the public board name for Greenhouse/Lever. Never a password.")
    perm_read = forms.BooleanField(required=False, initial=True, label="Read")
    perm_prepare = forms.BooleanField(required=False, initial=True, label="Prepare")
    perm_write = forms.BooleanField(required=False, label="Write")
    perm_submit = forms.BooleanField(required=False, label="Submit (only if the provider officially supports it)")

    FORBIDDEN = ("password", "passwd", "otp", "cookie", "session", "recovery")

    def __init__(self, provider, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider = provider
        labels = dict(provider.METHODS)
        self.fields["method"].choices = [(m, labels[m]) for m in provider.connection_methods]
        if not provider.can_submit:
            self.fields["perm_submit"].disabled = True

    def clean_account_identifier(self):
        v = self.cleaned_data["account_identifier"].strip()
        if any(w in v.lower() for w in self.FORBIDDEN) or len(v.split()) > 1:
            raise ValidationError("Enter an identifier only (no passwords, codes or cookies).")
        if self.provider.connector in ("greenhouse", "lever"):
            import re
            if not re.match(r"^[a-z0-9][a-z0-9-]{0,63}$", v.lower()):
                raise ValidationError("Use the board name from the URL, e.g. boards.greenhouse.io/<name>.")
            v = v.lower()
        return v

    def permissions(self):
        d = self.cleaned_data
        return {"read": d["perm_read"], "prepare": d["perm_prepare"], "write": d["perm_write"],
                "submit": bool(d["perm_submit"]) and self.provider.can_submit}


class TaskForm(forms.Form):
    device = forms.ModelChoiceField(queryset=None)
    tool = forms.ChoiceField()
    payload = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), required=False, initial="{}",
                              help_text="JSON object with the tool arguments")

    def __init__(self, *args, **kwargs):
        from .models import AgentDevice
        from .tools import LOCAL_TOOLS, REGISTRY
        super().__init__(*args, **kwargs)
        self.fields["device"].queryset = AgentDevice.objects.filter(is_revoked=False)
        self.fields["tool"].choices = [(n, f"{n} ({t.level})") for n, t in REGISTRY.items()] + [(n, f"{n} (local)") for n in LOCAL_TOOLS]

    def clean_payload(self):
        import json
        try:
            data = json.loads(self.cleaned_data["payload"] or "{}")
        except ValueError:
            raise ValidationError("Invalid JSON.")
        if not isinstance(data, dict):
            raise ValidationError("Must be a JSON object.")
        return data
