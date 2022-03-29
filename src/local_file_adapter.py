"""
Enable to load file with request with url
"""
import os
import sys

from io import BytesIO

import requests


if sys.version_info.major < 3:
    from urllib import url2pathname  # pylint: disable=E0611
else:
    from urllib.request import url2pathname


class LocalFileAdapter(requests.adapters.BaseAdapter):
    """Protocol Adapter to allow Requests to GET file:// URLs

    @todo: Properly handle non-empty hostname portions.
    """

    @staticmethod
    def _chkpath(method, path):
        """Return an HTTP status for the given filesystem path."""
        code, message = 200, "OK"
        if method.lower() in ('put', 'delete'):
            code, message = 501, "Not Implemented"
        elif method.lower() not in ('get', 'head'):
            code, message = 405, "Method Not Allowed"
        elif os.path.isdir(path):
            code, message = 400, "Path Not A File"
        elif not os.path.isfile(path):
            code, message = 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            code, message = 403, "Access Denied"
        return code, message

    def send(self, req, **kwargs):  # pylint: disable=unused-argument disable=arguments-differ
        """Return the file specified by the given request

        @type req: C{PreparedRequest}
        @todo: Should I bother filling `response.headers` and processing
               If-Modified-Since and friends using `os.stat`?
        """
        path = os.path.normcase(os.path.normpath(url2pathname(req.path_url)))
        response = requests.Response()

        response.status_code, response.reason = self._chkpath(req.method, path)
        if response.status_code == 200 and req.method.lower() != 'head':
            try:
                with open(path, 'rb') as file:
                    response.raw = BytesIO(file.read())
            except (OSError, IOError) as err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url

        response.request = req
        response.connection = self

        return response

    def close(self):
        pass
