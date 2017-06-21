# -*- coding: utf-8 -*-

import socket
from HttpMessage import HttpResponse
from HttpMessage import HttpRequest
from HttpDecoder import HttpDecoder
from robot.api import logger


class HttpServer():
    """Описывает поведение Http сервера."""
    __SERVER_HOST = ''
    __DEFAULT_PORT = 80
    __DEFAULT_TIMEOUT = 0
    __DEFAULT_MAX_CNN = 10
    __DEFAULT_READ_SIZE = 16384

    def __init__(self):
        self.port = HttpServer.__DEFAULT_PORT
        self.timeout = HttpServer.__DEFAULT_TIMEOUT
        self.isStarted = False
        self.server = None
        self.clients = {}
        self.max_cnn = HttpServer.__DEFAULT_MAX_CNN
        self.message_max_size = HttpServer.__DEFAULT_READ_SIZE

    def __check_server_not_started(self):
        assert not self.isStarted, "Http server has been already started."

    def __check_server_started(self):
        assert self.isStarted, "Http server has not been started yet."

    def set_options(self, _port=__DEFAULT_PORT, _timeout=__DEFAULT_TIMEOUT, _max_cnn=__DEFAULT_MAX_CNN, _message_max_size=__DEFAULT_READ_SIZE):
        """Установка опций сервера, дефалтовый порт = 80, _timeout - определяет таймауты сокета, дефалтовое значение тайм-аута равен 10 сек.
        _max_cnn - максимальное значение подключенных к серверу одновременно коннекций, значение по умолчанию = 10.
        _message_max_size - максимальное количеество читаемых из сокета байт.По дефолту значение 16384."""
        assert (_port is None or isinstance(_port, int)), "Port must be int value."
        self.port = _port
        self.timeout = _timeout
        self.max_cnn = _max_cnn
        self.message_max_size = _message_max_size

    def start_server(self):
        """Старт HTTP сервера."""
        self.__check_server_not_started()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HttpServer.__SERVER_HOST, self.port))
        self.server.listen(self.max_cnn)
        self.server.settimeout(self.timeout)
        self.server.setblocking(True)
        # стартуем поток в котором обрабатываются входящие соединения
        self.isStarted = True

    def accept_connection(self, _num=1):
        """Принимает соединение._num - количество соединений, которые ожидается принять, по умолчанию _num=1."""
        assert (isinstance(_num, int) and _num > 0 and _num <= self.max_cnn), "Num parameter must be int and more then 0."
        self.__check_server_started()
        i = 1
        l = []
        while i <= _num:
            try:
                (conn, (ip, port)) = self.server.accept()
                i += 1
            except socket.timeout:
                continue
            except:
                raise
            else:
                address = u"{ip}:{port}".format(ip=ip, port=port)
                self.clients[address] = conn
                l.append(address)
        return l

    def __stop_server(self):
        if not self.isStarted:
            return
        self.isStarted = False
        self.server.close()
        #ожидаем завершения потока
        self.clients.clear()

    def stop_server(self):
        """Остановка HTTP сервера. Повторный вызов игнорируется. Вызов при не запущенном сервере игнорируется."""
        self.__stop_server()

    def send(self, _cnn_alias, _resp):
        """Посылка ответа на запрос _resp через коннекцию с алиасом _cnn_alias. Объект _resp должен быть типа HttpResponse."""
        assert isinstance(_resp, HttpResponse), "Response must be HttpResponse."
        assert isinstance(_cnn_alias, unicode), "Alias for connection should be unicode string."
        self.__check_server_started()
        req_str = _resp.formatResponse()
        try:
            #выберем коннекцию и совершим действие
            cnn = self.clients[_cnn_alias]
            assert cnn is not None, "Connection for send was not found"
            cnn.sendall(req_str)
        except Exception as ex:
            logger.warn("Error occured during sending http response: [%s]" % ex.message)
            self.__stop_server()

    def recv(self, _cnn_alias):
        """Выполняет операцию чтения из сокета с алиасом _cnn_alias. Возвращаемый объект имеет тип HttpRequest и представляет
        собой полученный запрос."""
        self.__check_server_started()
        cnn = self.clients[_cnn_alias]
        assert cnn is not None, "Unknown connection with alias {alias}".format(alias=_cnn_alias)
        b = bytearray(self.message_max_size)
        num_bytes = cnn.recv_into(b)
        if num_bytes == 0:
            return None
        if num_bytes > self.message_max_size:
            raise Exception("Number of received bytes more than max message size")
        return HttpDecoder.decode_request(b, num_bytes, _cr_cl=False)

    def recv_available(self):
        """Выполняет поиск клиента, для которого в буфере на чтение лежит запрос. Возвращает alias соединения и полученное сообщение.
        В случае отсутвия сообщения возвращает None."""
        for address, cnn in self.clients.iteritems():
            try:
                cnn.setblocking(0)
                msg = self.recv(address)
                if msg == None:
                    continue
                return address, msg
            except socket.error as ex:
                continue
            finally:
                cnn.setblocking(1)

    def set_response_body(self, _resp, _body):
        """Установка тела ответа на запрос. При этом _resp имеет тип HttpResponse, _body имеет тип unicode.
        При задании _body как None - происходит сброс Content-Length = 0. При установке тела сообщения происходит вычисление
        и установка Content-Length."""
        assert isinstance(_resp, HttpResponse), "Incoming parameter should be HttpResponse"
        _resp.set_body(_body)

    def get_request_body(self, _req):
        """Получение тела запроса. Объект _req должен иметь тип HttpRequest."""
        assert isinstance(_req, HttpRequest), "Incoming parameter should be HttpRequest"
        return _req.get_body()

    def set_response_header(self, _resp, _name, _value = None):
        """Установка заголовка в ответе на запрос. _resp - ответ на запрос, _name - имя заголовка, _value - значение заголовка.
        Если _value=None происходит удаление заголовка. При установке Content-Type происходит вычисление и установка
        заголовка Content-Length в зависимости от кодировки."""
        assert isinstance(_resp, HttpResponse), "Incoming parameter should be HttpResponse"
        _resp.set_header(_name, _value)

    def set_response_headers(self, _resp, _dict):
        """Для объекта _resp типа HttpResponse происходит установка заголовков. При этом _dict - словарь ["заголовк" : "значение"].
        Для каждого объекта словаря происходит вызов set_response_header."""
        assert isinstance(_resp, HttpResponse), "Incoming parameter should be HttpResponse"
        _resp.set_headers(_dict)

    def check_request_header(self, _req, _name, _value):
        """Для полученного запроса _req типа HttpRequest происходит проверка заголовка _name на соответсвие _value.
        Для каждого объекта словаря происходит вызов set_response_header. Если _value = None - подразумевается что
        заголовок отсутсвует в запросе."""
        assert isinstance(_req, HttpRequest), "Incoming parameter should be HttpRequest"
        _req.check_header(_name, _value)

    def create_response(self, _version, _rc):
        """Создание ответа на запрос. Возвращается объект HttpResponse. У объекта автоматически проставляется Content-Length = 0.
        _version - версия протокола(1.0 или 1.1), _rc - HTTP result code."""
        resp = HttpResponse(True)
        HttpDecoder.check_version(_version)
        resp.set_version(_version)
        resp.set_result_code(_rc)
        return resp

    def check_request_version(self, _req, _version):
        """Проверка входного версии входящего запроса, поддерживаемые версии 1.0 и 1.1.
        Параметр _req - полученный запрос типа HttpRequest, _version - версия протокола."""
        assert isinstance(_req, HttpRequest), "Incoming parameter should be HttpRequest"
        HttpDecoder.check_version(_version)
        _req.check_version(_version)

    def check_request_method(self, _req, _method):
        """Проверка HTTP метода.Параметр _req - полученный запрос типа HttpRequest, _method - метод."""
        assert isinstance(_req, HttpRequest), "Incoming parameter should be HttpRequest"
        HttpDecoder.check_method(_method)
        _req.check_method(_method)

    def check_request_path(self, _req, _path):
        """Проверка url запроса.Параметр _req - полученный запрос типа HttpRequest, _path - url."""
        assert isinstance(_req, HttpRequest), "Incoming parameter should be HttpRequest"
        _req.check_path(_path)

def __unit_tests():
    server = HttpServer()
    server.set_options(8085)
    server.start_server()
    server.stop_server()

__unit_tests()