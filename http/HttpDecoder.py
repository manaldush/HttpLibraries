# -*- coding: utf-8 -*-

from HttpMessage import HttpRequest
from HttpMessage import HttpResponse
from robot.api import logger

class HttpDecoder():

    __SERVER_HOST = ''
    __DEFAULT_PORT = 80
    __DEFAULT_TIMEOUT = 0
    __DEFAULT_MAX_CNN = 10
    __DEFAULT_NAME = u"http-server-emulation"
    __HTTP_METHODS = {}
    __HTTP_METHODS[u"GET"] = True
    __HTTP_METHODS[u"POST"] = True
    __HTTP_METHODS[u"PUT"] = True
    __HTTP_METHODS[u"OPTIONS"] = True
    __HTTP_METHODS[u"HEAD"] = True
    __HTTP_METHODS[u"DELETE"] = True
    __HTTP_METHODS[u"TRACE"] = True
    __HTTP_METHODS[u"CONNECT"] = True
    __HTTP_VERSIONS = {u"1.0": True, u"1.1": True}


    def __init__(self):
        pass

    @staticmethod
    def __parse_version(_version):
        v = _version.split(u"/")
        assert len(v) == 2, "Unknown protocol: error during parsing version string {version}".format(version=_version)
        assert v[0] == u"HTTP", "Unknown protocol {protocol}".format(protocol=v[0])
        assert HttpDecoder.__HTTP_VERSIONS[v[1]], "Unsupported protocol version {version}".format(version=v[1])
        return v[1]

    @staticmethod
    def __parse_header(_header, _headers_dict):
        header_str = bytearray(_header).decode("utf-8")
        kv = header_str.split(u":",1)
        assert len(kv) == 2, "Http error parsing header string {header}".format(header=header_str)
        logger.info("{key} : {value}".format(key=unicode(kv[0]), value=unicode(kv[1]).strip()))
        _headers_dict[unicode(kv[0])] = unicode(kv[1]).strip()

    @staticmethod
    def __parse_req_line(_header, _cr_cl):
        header_str = bytearray(_header).decode("utf-8")
        l = header_str.split(u" ")
        if len(l) != 3:
            raise Exception("Protocol error during parsing first line: {line}".format(line=header_str))
        version = HttpDecoder.__parse_version(unicode(l.pop()))
        path = unicode(l.pop())
        method = unicode(l.pop())
        assert HttpDecoder.__HTTP_METHODS[method], "Unknown HTTP method {method}".format(method=method)
        return HttpRequest(method, path, version,_cr_cl)

    @staticmethod
    def __parse_resp_line(_header, _cr_cl):
        header_str = bytearray(_header).decode("utf-8")
        l = header_str.split(u" ", 1)
        if len(l) != 2:
            raise Exception("Protocol error")
        rc = unicode(l.pop())
        version = HttpDecoder.__parse_version(unicode(l.pop()))
        resp=HttpResponse(_cr_cl)
        resp.set_version(version)
        resp.set_result_code(rc)
        return resp

    @staticmethod
    def __parse_headers(_pack, _num_bytes, _factory, _cr_cl):
        i = 0
        cr = False
        crlf = False
        end = False
        header = []
        protocol_header = False
        headers_dict = {}
        pack = None
        while i < _num_bytes:
            b = _pack[i]
            if cr and crlf and b == 10:
                #найден конец заголовков HTTP = i
                end = True
                i += 1
                break
            if cr and b == 10:
                if protocol_header:
                    HttpDecoder.__parse_header(header, headers_dict)
                else:
                    pack = _factory(header, _cr_cl)
                    protocol_header = True
                header = []
                crlf = True
                cr = False
                i += 1
                continue
            if cr and b != 10:
                raise Exception("Http protocol error: wait LF after CR")
            if b == 13:
                cr = True
                i += 1
                continue
            crlf=False
            header.append(b)
            i += 1
        if end:
            pack.set_headers(headers_dict)
            return pack, i
        else:
            raise Exception("Http protocol error: end of HTTP headers was not found")

    @staticmethod
    def decode_request(_byte_req, _num_bytes, _cr_cl=True):
        factory = lambda header, _cr_cl: HttpDecoder.__parse_req_line(header, _cr_cl)
        req, i = HttpDecoder.__parse_headers(_byte_req, _num_bytes, factory, _cr_cl)
        byte_body = []
        while i < _num_bytes:
            byte_body.append(_byte_req[i])
            i+=1
        req.set_byte_body(bytearray(byte_body))
        return req

    @staticmethod
    def decode_response(_byte_req, _num_bytes, _cr_cl=True):
        factory = lambda header, _cr_cl: HttpDecoder.__parse_resp_line(header, _cr_cl)
        resp, i = HttpDecoder.__parse_headers(_byte_req, _num_bytes, factory, _cr_cl)
        byte_body = []
        while i < _num_bytes:
            byte_body.append(_byte_req[i])
            i+=1
        resp.set_byte_body(bytearray(byte_body))
        return resp

    @staticmethod
    def check_version(_version):
        assert HttpDecoder.__HTTP_VERSIONS[_version], "Illegal http protocol version {version}".format(version=_version)

    @staticmethod
    def check_method(_method):
        assert HttpDecoder.__HTTP_METHODS[_method], "Illegal http protocol method {method}".format(method=_method)
