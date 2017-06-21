# -*- coding: utf-8 -*-

# Http коды ответа и их описание
# 1xx: Informational (информационные):
HTTP_CONTINUE =  u"100 Continue"
HTTP_SWITCHING_PROTOCOLS = u"101 Switching Protocols"
HTTP_PROCESSING = u"102 Processing"

# 2xx: Success (успешно):
HTTP_OK = u"200 OK"
HTTP_CREATED = u"201 Created"
HTTP_ACCEPTED = u"202 Accepted"
HTTP_NON_AUTHORITATIVE_INFORMATION = u"203 Non-Authoritative Information"
HTTP_NO_CONTENT = u"204 No Content"
HTTP_RESET_CONTENT = u"205 Reset Content"
HTTP_PARTIAL_CONTENT = u"206 Partial Content"
HTTP_MULTI_STATUS = u"207 Multi-Status"

# 3xx: Redirection (перенаправление):
HTTP_MULTIPLE_CHOICES = u"300 Multiple Choices"
HTTP_MOVED_PERMANENTLY = u"301 Moved Permanently"
HTTP_FOUND = u"302 Found"
HTTP_SEE_OTHER = u"303 See Other"
HTTP_NOT_MODIFIED = u"304 Not Modified"
HTTP_USE_PROXY = u"305 Use Proxy"
HTTP_TEMPORARY_REDIRECT = u"307 Temporary Redirect"

# 4xx: Client Error (ошибка клиента):
HTTP_BAD_REQUEST = u"400 Bad Request"
HTTP_UNAUTHORIZED = u"401 Unauthorized"
HTTP_PAYMENT_REQUIRED = u"402 Payment Required"
HTTP_FORBIDDEN = u"403 Forbidden"
HTTP_NOT_FOUND = u"404 Not Found"
HTTP_METHOD_NOT_ALLOWED = u"405 Method Not Allowed"
HTTP_ACCEPTABLE = u"406 Not Acceptable"
HTTP_PROXY_AUTHENTICATION_REQUIRED = u"407 Proxy Authentication Required"
HTTP_REQUEST_TIMEOUT = u"408 Request Timeout"
HTTP_CONFLICT = u"409 Conflict"
HTTP_GONE = u"410 Gone"
HTTP_LENGTH_REQUIRED = u"411 Length Required"
HTTP_PRECONDITION_FAILED = u"412 Precondition Failed"
HTTP_REQUEST_ENTITY_TOO_LARGE = u"413 Request Entity Too Large"
HTTP_REQUEST_URI_TOO_LARGE = u"414 Request-URI Too Large"
HTTP_UNSUPPORTED_MEDIA_TYPE = u"415 Unsupported Media Type"
HTTP_REQUESTED_RANGE_NOT_SATISFIABLE = u"416 Requested Range Not Satisfiable"
HTTP_EXPECTATION_FAILED = u"417 Expectation Failed"

# 5xx: Server Error (ошибка сервера):
HTTP_INTERNAL_SERVER_ERROR = u"500 Internal Server Error"
HTTP_NOT_IMPLEMENTED = u"501 Not Implemented"
HTTP_BAD_GATEWAY = u"502 Bad Gateway"
HTTP_SERVICE_UNAVAILABLE = u"503 Service Unavailable"
HTTP_GATEWAY_TIMEOUT = u"504 Gateway Timeout"
HTTP_VERSION_NOT_SUPPORTED = u"505 HTTP Version Not Supported"