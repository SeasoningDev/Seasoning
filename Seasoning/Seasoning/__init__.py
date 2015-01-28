from django.conf import settings

def local_test_context_processor(request):
    return {'LOCAL_TEST': settings.LOCAL_TEST}