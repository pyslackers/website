from celery.result import AsyncResult
from django.http.response import HttpResponse, JsonResponse


def task_result_view(request, task_id):
    """Generic way to retrieve task results
    as JSON data."""
    # task_id = request.GET.get('task_id')
    result = AsyncResult(str(task_id))
    if result.ready():
        res = result.get()
        if not isinstance(res, (list, dict, tuple)):
            res = {}
        return JsonResponse(res)
    return HttpResponse(status=204)
