from rest_framework.response import Response

SUCCESS = 'success'
FAILED = 'fail'


def response(status, data, http_status):
    r = {
        'status': status,
        'data': data
    }
    return Response(data=r, status=http_status)
