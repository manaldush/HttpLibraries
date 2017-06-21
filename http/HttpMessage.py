# -*- coding: utf-8 -*-

import sys
import HttpCodes
from robot.api import logger

class HttpMessage:
    """Класс содержит описание набора базовых сущностей и операций для всех HTTP запросов"""

    __CRLF = u"\r\n"
    __ContentLength = u"Content-Length"
    __ContentType = u"Content-Type"
    __ContentLengthDefaultVal = u"0"
    __DefaultCharset = "utf-8"

    def __init__(self, _cr_cl):
        self.__body = None
        self.__create_content_len = _cr_cl
        if self.__create_content_len:
            self.__headers = {HttpMessage.__ContentLength : HttpMessage.__ContentLengthDefaultVal}
        else :
            self.__headers = {}
        self.__charset = HttpMessage.__DefaultCharset
        self.__encoded_body = None

    @staticmethod
    def __check_header_name(_name):
        assert _name is not None, "Http header name can not be None"
        assert type(_name) == unicode, "Http header name must be unicode string type"

    @staticmethod
    def __parse_encoding(_content_type):
        attrs = _content_type.split(u';')
        i = 0
        while i < len(attrs):
            attr = attrs[i].strip()
            if attr.startswith(u"charset"):
                kv = attr.split(u'=')
                if len(kv) == 2:
                    return kv[1]
            i += 1
        return HttpMessage.__DefaultCharset

    def set_body(self, _body=None):
        """Заполняет тело HTTP сообщения, в случае, если параметр _body не передан, значение устанавливается в None.
        При этом происходит выставление поля Content-Length в заголовках."""
        if _body is None:
            self.__body = None
            self.__encoded_body = None
            if self.__create_content_len:
                self.set_header(HttpMessage.__ContentLength, HttpMessage.__ContentLengthDefaultVal)
        else:
            assert type(_body) == unicode, "Http body should be unicode string type"
            self.__body = _body
            self.__encoded_body = self.__body.encode(self.__charset)
            if self.__create_content_len:
                self.set_header(HttpMessage.__ContentLength, unicode(len(self.__encoded_body)))

    def __check_body_length(self, _byte_body):
        ln = self.__headers.get(HttpMessage.__ContentLength, 0)
        ln = int(ln)
        if ln < len(_byte_body):
            raise Exception("Http protocol error, was received only {ln_recv}, but content-length = {ln}".format(ln_recv=len(_byte_body), ln=ln))
        if ln > len(_byte_body):
            raise Exception("Http protocol error, was received {ln_recv}, but content-length = {ln}".format(ln_recv=len(_byte_body), ln=ln))

    def set_byte_body(self, _byte_body):
        if len(_byte_body) > 0:
            self.__check_body_length(_byte_body)
            self.__encoded_body = _byte_body.decode(self.__charset)
            self.__body = unicode(self.__encoded_body)

    def get_body(self):
        """Возвращает тело HTTP сообщения."""
        return self.__body

    def set_header(self, _name, _value = None):
        """Добавляет заголовок в список HTTP заголовков. В случае если значение None, соответсвующий header удаляется"""
        HttpMessage.__check_header_name(_name)
        if _value == None:
            #тогда удалим значение
            self.__headers.pop(_name, None)
        else:
            assert type(_value) == unicode, "Http header value must be unicode string type"
            if _name == HttpMessage.__ContentType:
                encoding = HttpMessage.__parse_encoding(_value)
                self.__charset = encoding
                self.set_body(self.__body)
            self.__headers[_name] = _value.strip()

    def set_headers(self, _dict):
        """Получает на вход словарь заголовков ввиде {"имя заголовка" = "значение заголовка"} и обновляет список заголовков сообщения"""
        assert _dict is not None, "Http headers dictionary can not be None"
        assert type(_dict) == dict, "Http headers dictionary should be dict type"
        assert len(_dict) > 0, "Http headers dictionary length should be more than 0"
        for key, value in _dict.iteritems():
            self.set_header(key, value)

    def check_header(self, _name, _value):
        """Проверяет значение Http header, если параметр _value устанволен в значение None - подразумевается что header с таким имененм не существует."""
        HttpMessage.__check_header_name(_name)
        if _value == None:
            assert self.__headers.get(_name, None) is None, "Header with name {name} should not be in Http headers".format(name = _name)
        else:
            value = self.__headers.get(_name, None)
            assert _value == value, "Header with name {name} does not have value {value}".format(name=_name, value = _value)

    def format(self):
        """Используется для формирования строки из сообщения"""
        if self.__body is None:
            return self.__format_headers()
        else:
            return self.__format_headers() + self.__format_body()

    def __format_headers(self):
        assert len(self.__headers) > 0, "Http headers dictionary length should be more than 0"
        headers = None
        for key, value in self.__headers.iteritems():
            header = u"{key}: {value}".format(key = key, value = value)
            header = header + HttpMessage.__CRLF
            if headers is None:
                headers = header
            else:
                headers = headers + header
        return (HttpMessage.__CRLF + headers + HttpMessage.__CRLF).encode('utf-8')

    def __format_body(self):
        return self.__encoded_body


class HttpResponse(HttpMessage):

    __DEFAULT_HTTP_VERSION = u"1.1"

    def __init__(self, _cr_cl):
        HttpMessage.__init__(self, _cr_cl)
        self.__rc = HttpCodes.HTTP_ACCEPTED
        self.__version = HttpResponse.__DEFAULT_HTTP_VERSION

    def set_version(self, _version):
        """Установка HTTP версии в ответе."""
        assert _version is not None, "Http version can not be None"
        assert isinstance(_version, unicode), "Http version parameter should be unicode string"
        self.__version = _version

    def set_result_code(self, _rc):
        """Установка HTTP RC в ответе."""
        assert _rc is not None, "Http result code can not be None"
        assert isinstance(_rc, unicode), "Http result code parameter should be unicode string"
        self.__rc = _rc

    def check_version(self, _version):
        assert self.__version == _version, "Http versions are not equal: {v1} != {v2}".format(v1=self.__version, v2=_version)

    def check_rc(self, _rc):
        assert self.__rc == _rc, "Http result codes are not equal: {rc1} != {rc2}".format(rc1=self.__rc, rc2=_rc)

    def formatResponse(self):
        """Приведение к формату строки HTTP ответа."""
        return (u"HTTP/{version} {rc}".format(version=self.__version, rc=self.__rc)).encode('utf-8') + self.format()


class HttpRequest(HttpMessage):

    def __init__(self, _method, _path, _version, _cr_cl):
        HttpMessage.__init__(self, _cr_cl)
        self.__validate_method(_method)
        self.__validate_path(_path)
        self.__validate_version(_version)
        self.__method = _method
        self.__path = _path
        self.__version = _version

    @staticmethod
    def __validate_method(_method):
        assert _method is not None, "Http method should not be None"
        assert isinstance(_method, unicode), "Http method should be unicode string"

    @staticmethod
    def __validate_path(_path):
        assert _path is not None, "Http path should not be None"
        assert isinstance(_path, unicode), "Http path should be unicode string"

    @staticmethod
    def __validate_version(_version):
        assert _version is not None, "Http version should not be None"
        assert isinstance(_version, unicode), "Http version should be unicode string"

    def __check_method(self, _method):
        HttpRequest.__validate_method(_method)
        assert self.__method == _method, "Methods are not equal: received = {v1}, waited = {v2}".format(v1=self.__method, v2=_method)

    def __check_path(self, _path):
        HttpRequest.__validate_path(_path)
        assert self.__path == _path, "Paths are not equal: received = {v1}, waited = {v2}".format(v1=self.__path,v2=_path)

    def __check_version(self, _version):
        HttpRequest.__validate_version(_version)
        assert self.__version == _version, "Versions are not equal: received = {v1}, waited = {v2}".format(v1=self.__version, v2=_version)

    def check_method(self, _method):
        """Проверка HTTP метода."""
        self.__check_method(_method)

    def check_path(self, _path):
        """Проверка HTTP path."""
        self.__check_path(_path)

    def check_version(self, _version):
        """Проверка HTTP версии."""
        self.__check_version(_version)

    def formatRequest(self):
        return (u"{method} {path} HTTP/{version}".format(method=self.__method, path=self.__path, version=self.__version)).encode('utf-8') + self.format()

def __unit_tests():
    httpMessage = HttpMessage(True)
    #1. проверим наличие http header Content-Length со значением 0
    httpMessage.check_header(u"Content-Length", u"0")
    # 2. проверим добавление http header Test-Header со значением test
    httpMessage.set_header(u"Test-Header", u"test")
    httpMessage.check_header(u"Test-Header", u"test")
    # 3. проверим добавление списка http headers
    httpMessage.set_headers({u"Test-Header_1" : u"test", u"Test-Header_2" : u"test"})
    httpMessage.check_header(u"Test-Header_1", u"test")
    httpMessage.check_header(u"Test-Header_2", u"test")
    #4. проверим отсутствие header
    httpMessage.check_header(u"Test-Header_None", None)
    #5 удалим один из header
    httpMessage.set_header(u"Test-Header", None)
    httpMessage.check_header(u"Test-Header", None)
    #6. установим body HTTP запроса
    httpMessage.set_body(u"test body")
    assert httpMessage.get_body() == u"test body", "Check message body"
    httpMessage.check_header(u"Content-Length", unicode(9))
    #7. форматируем сообщение в строку
    assert httpMessage.format() == '\r\nTest-Header_2: test\r\nContent-Length: 9\r\nTest-Header_1: test\r\n\r\ntest body', "Check formatted message error"

    #8. проверка HttpResponse
    httpResponse = HttpResponse(True)
    httpResponse.set_version(u"1.1")
    httpResponse.set_result_code(HttpCodes.HTTP_BAD_GATEWAY)
    httpResponse.set_header(u"Test-Header", u"test")
    httpResponse.set_body(u"test body")
    assert httpResponse.formatResponse() == 'HTTP/1.1 502 Bad Gateway\r\nContent-Length: 9\r\nTest-Header: test\r\n\r\ntest body', "Check formatted message error"

    #9. Проверим изменение кодировки тела ообщения
    httpResponse.set_header(u"Content-Type", u"text/html; charset=iso-8859-1")
    assert httpResponse.formatResponse() == 'HTTP/1.1 502 Bad Gateway\r\nContent-Length: 9\r\nContent-Type: text/html; charset=iso-8859-1\r\nTest-Header: test\r\n\r\ntest body', "Check formatted message error"

    #10. проверка HttpRequest
    httpRequest = HttpRequest(u"GET", u"/www.test.ru", u"1.1",True)
    httpRequest.check_method(u"GET")
    httpRequest.check_path(u"/www.test.ru")
    httpRequest.check_version(u"1.1")


__unit_tests()