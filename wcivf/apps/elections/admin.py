from django.contrib import admin

from .models import Election, Post, VotingSystem


class ElectionAdmin(admin.ModelAdmin):
    list_filter = ("election_type", "voting_system")


class PostAdmin(admin.ModelAdmin):
    list_display = ("label",)
    list_filter = ("organization",)


admin.site.register(Election, ElectionAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(VotingSystem)
