from django.templatetags.static import static
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.text import slugify

from elections.models import Post
from people.models import Person, PersonPost


class DummyCandidacy(PersonPost):
    post = Post(label="Made-Up-Ward")

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person.featured_candidacy = self


class DummyPerson(Person):
    intro_template = "people/includes/intros/base.html"

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.statement_to_voters = render_to_string(
            template_name=f"people/dummy_statements/{self.name_slug}.txt"
        )
        self.photo_url = static(f"images/{self.name_slug}.png")

    @property
    def name_slug(self):
        return slugify(self.name)

    @property
    def current_or_future_candidacies(self):
        return True

    def get_absolute_url(self):
        return reverse(
            viewname="dummy-profile", kwargs={"name": self.name_slug}
        )
