from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from .models import User, Organization

admin.site.register(User, UserAdmin)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "verification_status", "verified_at")
    list_filter = ("verification_status",)
    search_fields = ("name", "user__username", "user__email")
    readonly_fields = ("verified_at",)
    actions = ("approve_organizations", "reject_organizations")

    @admin.action(description="Approve selected organizations")
    def approve_organizations(self, request, queryset):
        queryset.update(
            verification_status=Organization.VERIFICATION_STATUS_APPROVED,
            verified_at=timezone.now(),
            rejection_reason="",
        )

    @admin.action(description="Reject selected organizations")
    def reject_organizations(self, request, queryset):
        queryset.update(
            verification_status=Organization.VERIFICATION_STATUS_REJECTED,
            verified_at=None,
        )

    def save_model(self, request, obj, form, change):
        if obj.verification_status == Organization.VERIFICATION_STATUS_APPROVED and not obj.verified_at:
            obj.verified_at = timezone.now()
            obj.rejection_reason = ""
        elif obj.verification_status != Organization.VERIFICATION_STATUS_APPROVED:
            obj.verified_at = None
        super().save_model(request, obj, form, change)
