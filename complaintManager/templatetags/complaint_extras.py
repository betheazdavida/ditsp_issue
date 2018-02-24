from django import template

register = template.Library()


@register.filter
def is_lead_by(complaint, user):
    return user.member.isLeaderOf(complaint)
