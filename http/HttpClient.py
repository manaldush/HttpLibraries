# -*- coding: utf-8 -*-

import socket
from HttpMessage import HttpRequest
from HttpMessage import HttpResponse
from HttpDecoder import HttpDecoder

class HttpClient():
    """Описывает логику работы клиентского HTTP соединения."""

    __DEFAULT_READ_SIZE = 16384

    def __init__(self):
        self.__port = None
        self.__host = None
        self.__cnn = None
        self.__is_opened = False
        self.__is_configured = False
        self.__message_max_size = HttpClient.__DEFAULT_READ_SIZE

    def __check_is_not_configured(self):
        assert not self.__is_configured, "Connection has been already configure"

    def __check_is_configured(self):
        assert self.__is_configured, "Connection has not been configured yet"

    def __check_is_opened(self):
        assert self.__is_opened, "Connection has not been opened yet"

    def __check_is_not_opened(self):
        assert not self.__is_opened, "Connection has been opened already"

    def set_options(self, _port, _host=u"127.0.0.1", _message_max_size=__DEFAULT_READ_SIZE):
        """Установка параметров настройки. _port - порт подключения, _host - адрес подключения(дефолтовое значение 127.0.0.1),
        _message_max_size - максимальное количество читаемых байтов из буфера(по умолчанию 16384)."""
        self.__check_is_not_configured()
        self.__port = _port
        self.__host = _host
        self.__is_configured = True
        self.__message_max_size=_message_max_size

    def open_connection(self):
        """Открывает соединение с хостом с опциями, выставленными при вызове set_options."""
        self.__check_is_configured()
        self.__check_is_not_opened()
        self.__cnn=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__cnn.connect((self.__host, self.__port))
        self.__is_opened = True

    def close_connection(self):
        """Закрывает клиентское соединение. Повторный вызов игнорируется. Вызов при закрытом соединении игнорируется."""
        if not self.__is_opened:
            return
        self.__cnn.close()
        self.__is_opened = False

    def send_request(self, _req):
        """Посылка запроса через клиентскую коннекцию. _req запрос типа HttpRequest."""
        assert isinstance(_req, HttpRequest), "Incoming object must be type = HttpRequest"
        self.__check_is_configured()
        self.__check_is_opened()
        self.__cnn.sendall(_req.formatRequest())

    def recv_response(self):
        """Возвращает полученный ответ на запрос. Возвращаемый объект имеет тип HttpResponse."""
        self.__check_is_configured()
        self.__check_is_opened()
        b = bytearray(self.__message_max_size)
        num_bytes = self.__cnn.recv_into(b)
        if num_bytes > self.__message_max_size:
            raise Exception("Number of received bytes more than max message size")
        return HttpDecoder.decode_response(b, num_bytes, _cr_cl=False)

    def create_request(self, _method, _path, _version):
        """Создание запроса для последующей посылки. Создаваемый объект будет иметь тип HttpRequest.
        _method - HTTP метод, _path - url, _version - версия протокола."""
        HttpDecoder.check_method(_method)
        HttpDecoder.check_version(_version)
        return HttpRequest(_method, _path, _version, True)

    def set_request_header(self, _req, _name, _value=None):
        """Установка HTTP заголовка в запросе _req, _name - имя заголовка, _value - значение заголовка. При установке
        заголовка значения заголовка в None - заголовок сбрасывается."""
        assert isinstance(_req, HttpRequest), "Incoming object must be type = HttpRequest"
        _req.set_header(_name, _value)

    def set_request_body(self, _req, _body):
        """Установка тела запроса. Объект запроса передается в _req и должен быть типа HttpRequest."""
        assert isinstance(_req, HttpRequest), "Incoming object must be type = HttpRequest"
        _req.set_body(_body)

    def check_response_version(self, _resp, _version):
        """Проверка версии ответа. Объект _resp представляется собой класс HttpResponse, т.е. ответ. _version - предполагаемая
        версия(возможные значения 1.0 и 1.1)"""
        assert isinstance(_resp, HttpResponse), "Incoming object must be type = HttpResponse"
        _resp.check_version(_version)

    def check_response_rc(self, _resp, _rc):
        """
        Проверка RC ответа.
        :param _resp: - ответ класса HttpResponse
        :param _rc: ожидаемый код ответа(предлагается использовать константы из HttpCodes)
        :return: в случае не соответсвия кидается исключение
        """
        assert isinstance(_resp, HttpResponse), "Incoming object must be type = HttpResponse"
        _resp.check_rc(_rc)

    def check_response_header(self, _resp, _name, _value):
        """
        Проверка HTTP заголовка ответа.
        :param _resp: - ответ класса HttpResponse
        :param _name: - имя заголовка
        :param _value: - ожидаемое значение, при None заголовка быть не должно
        :return: в случае не соответсвия кидается исключение
        """
        assert isinstance(_resp, HttpResponse), "Incoming object must be type = HttpResponse"
        _resp.check_header(_name, _value)

    def get_response_body(self, _resp):
        """
        Получение тела ответа.
        :param _resp: - ответ класса HttpResponse
        :return: тело
        """
        assert isinstance(_resp, HttpResponse), "Incoming object must be type = HttpResponse"
        return _resp.get_body()

def __unit_tests():
    response = HttpResponse(True)
    response.set_result_code(u"200 OK")
    response.set_version(u"1.1")
    response.set_header(u"key1", u"value")
    response.set_body(u"test_body")
    client = HttpClient()
    client.check_response_rc(response, u"200 OK")
    client.check_response_version(response, u"1.1")
    client.check_response_header(response, u"key1", u"value")
    assert u"test_body" == response.get_body(), "Body compare error"

__unit_tests()