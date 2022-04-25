from django.http import HttpResponse, HttpResponseForbidden
from django.views.generic import View, UpdateView
from django.utils.http import is_safe_url
from django.contrib import messages
from django.template.loader import render_to_string
from akismet import Akismet
from django.conf import settings

from .forms import FeedbackForm
from .models import Feedback


class FeedbackFormView(UpdateView):
    form_class = FeedbackForm
    template_name = "feedback/feedback_form_view.html"

    @property
    def is_spam(self):
        if not settings.AKISMET_API_KEY:
            return False

        akismet = Akismet(
            settings.AKISMET_API_KEY, blog=settings.AKISMET_BLOG_URL
        )
        return akismet.check(
            self.request.META["REMOTE_ADDR"],
            self.request.META["HTTP_USER_AGENT"],
            comment_content=self.request.POST.get("comments"),
        )

    def get_object(self, queryset=None):
        token = self.request.POST.get("token")
        try:
            return Feedback.objects.get(token=token)
        except Feedback.DoesNotExist:
            return Feedback(token=token)

    def get_success_url(self):

        messages.success(
            self.request,
            render_to_string(
                "feedback/feedback_thanks.html",
                request=self.request,
                context={"object": self.object},
            ),
            extra_tags="template",
        )

        if self.is_spam:
            self.object.flagged_as_spam = True
            self.object.save()
        if is_safe_url(self.object.source_url, allowed_hosts=None):
            return self.object.source_url
        else:
            return "/"


class RecordJsonFeedback(View):
    def post(self, request):
        found_useful = request.POST.get("found_useful")
        source_url = request.POST.get("source_url")
        token = request.POST.get("token")
        Feedback.objects.update_or_create(
            token=token,
            defaults={"found_useful": found_useful, "source_url": source_url},
        )
        return HttpResponse()
