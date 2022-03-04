from django import forms
from django.utils.translation import ugettext_lazy as _

from localflavor.gb.forms import GBPostcodeField


class PostcodeLookupForm(forms.Form):
    postcode = GBPostcodeField(label=_("Enter your postcode"))

    def __init__(self, autofocus=False, *args, **kwargs):
        super(PostcodeLookupForm, self).__init__(*args, **kwargs)
        if autofocus:
            self.fields["postcode"].widget.attrs["autofocus"] = u"autofocus"
