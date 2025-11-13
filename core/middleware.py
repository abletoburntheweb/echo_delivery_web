from django.shortcuts import render
from django.conf import settings
from django.core.cache import cache


class BlockSiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        block_enabled = cache.get('admin_setting_block_enabled', False)

        if (block_enabled and
                not request.path.startswith('/admin/') and
                not request.path.startswith('/static/') and
                not request.path.startswith('/media/') and
                request.path != '/login/' and
                not request.user.is_superuser):

            from .views import get_work_dates
            work_dates = get_work_dates()

            return render(request, 'site_blocked.html', {
                'work_dates': work_dates
            }, status=503)

        response = self.get_response(request)
        return response