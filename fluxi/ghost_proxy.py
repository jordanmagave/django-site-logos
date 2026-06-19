import requests
from django.http import StreamingHttpResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

GHOST_URL = "http://35.198.39.119:2368/blog"


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
def proxy(request, ghost_path=""):
    has_trailing_slash = ghost_path == "" and request.path.endswith("/")
    target = f"{GHOST_URL}/{ghost_path}" if ghost_path else GHOST_URL
    if has_trailing_slash:
        target = f"{target}/"

    headers = {
        "X-Forwarded-For": request.META.get("REMOTE_ADDR", ""),
        "X-Forwarded-Proto": "https",
        "X-Forwarded-Host": request.META.get("HTTP_HOST", "celogos.com.br"),
        "Accept": request.META.get("HTTP_ACCEPT", "*/*"),
        "Accept-Language": request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
        "Accept-Encoding": request.META.get("HTTP_ACCEPT_ENCODING", ""),
        "Cookie": request.META.get("HTTP_COOKIE", ""),
        "Content-Type": request.META.get("CONTENT_TYPE", ""),
        "Referer": request.META.get("HTTP_REFERER", ""),
        "User-Agent": request.META.get("HTTP_USER_AGENT", ""),
        "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
    }

    body = request.body if request.method in ("POST", "PUT", "PATCH") else None

    try:
        resp = requests.request(
            method=request.method,
            url=target,
            headers={k: v for k, v in headers.items() if v},
            params=request.GET,
            data=body,
            cookies=request.COOKIES,
            stream=True,
            timeout=30,
            allow_redirects=False,
        )
    except requests.RequestException as e:
        return HttpResponse(f"Erro no proxy: {e}", status=502)

    response = StreamingHttpResponse(
        streaming_content=resp.iter_content(8192),
        status=resp.status_code,
    )

    excluded = {"transfer-encoding", "content-encoding", "content-length"}
    for key, value in resp.headers.items():
        if key.lower() not in excluded:
            response[key] = value

    return response
