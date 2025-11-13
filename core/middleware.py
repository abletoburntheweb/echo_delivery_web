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
                not request.path.startswith(settings.STATIC_URL) and
                not request.path.startswith(settings.MEDIA_URL) and
                request.path != '/login/'):
            return render(request, 'site_blocked.html', status=503)

        response = self.get_response(request)
        return response