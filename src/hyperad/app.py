from requests.sessions import Session

from hyperad import constants
from hyperad.contents import Content


class App(Session):
    """ A extensive class of `requests.Session` which supports sending data in
    different formats.  `App` also provides some methods to process the
    response in many types.

    New methods:
    - `App.submit()`: is a substitution of `Session.request()`.
    - `App.c*()`: in which `*` is (`get`, `post`, `put`, ...), is substitutions
    of `Session.get()`, `Sesssion.post()`, `Session.put()`, ...

    Usage:
    >>> username = Field("username", "admin")
    >>> password = Field("password", "ratatatata")
    >>> form = MultiContent("login-form")
    >>> form.add(username, password)
    >>> app = App()
    >>> resp = app.cpost("http://some.url/login", form)
    """

    def crequest(self, method, url, content: Content, **kwargs):
        """ Submit some formated data to url.
        @param `method`: method for the new :class:`Request` object.
        @param `url`: URL for the new :class:`Request` object.
        @param `headers`: (optional) `dict` of HTTP Headers to send with\
            the :class:`Request`.
        @param `cookies`: (optional) `dict` or `CookieJar` object to send with\
            the :class:`Request`.
        @param auth: (optional) Auth `tuple` or `callable` to enable\
            Basic/Digest/Custom HTTP Auth.
        @param `timeout`: (optional) How long to wait for the server to send\
            data before giving up, as a `float`, or a :ref:`(connect timeout,\
            read timeout) <timeouts>` `tuple`.
        @param `allow_redirects`: (optional) Set to `True` by default.
        @param `proxies`: (optional) `dict` mapping protocol or protocol and\
            hostname to the URL of the proxy.
        @param `stream`: (optional) whether to immediately download the\
            response content.  Defaults to `False`.
        @param `verify`: (optional) Either a `bool`, in which case it controls\
            whether we verify the server's TLS certificate, or a `str`, in\
            which case it must be a path to a CA bundle to use.  Defaults to\
            `True`.  When set to `False`, requests will accept any TLS\
            certificate presented by the server, and will ignore hostname\
            mismatches and/or expired certificates, which will make your\
            application vulnerable to man-in-the-middle (MitM) attacks.\
            Setting verify to `False` may be useful during local development\
            or testing.
        @param `cert`: (optional) if `str`, path to ssl client cert file\
            (.pem).  If `tuple`, ('cert', 'key') pair.
        @rtype: `requests.Response`.
        """
        invalid_params = ("data", "json", "files", "params")
        for name in invalid_params:
            if name in kwargs.keys():
                raise ValueError("Don't use these parameters {}. They "
                "have already been included in `Content` object."
                .format(invalid_params)
                )

        parameters = content.build()

        headers = kwargs.pop("headers", None)
        if headers and ("headers" in parameters.keys()):
            parameters["headers"].update(headers)

        parameters.update(kwargs)

        return self.request(method, url, **parameters)

    def cget(self, url, content: Content, **kwargs):
        return self.crequest(constants.GET, url, content, **kwargs)
        
    def cpost(self, url, content: Content, **kwargs):
        return self.crequest(constants.POST, url, content, **kwargs)
        
    def cput(self, url, content: Content, **kwargs):
        return self.crequest(constants.PUT, url, content, **kwargs)
        
    def cdelete(self, url, content: Content, **kwargs):
        return self.crequest(constants.DELETE, url, content, **kwargs)
        
    def coptions(self, url, content: Content, **kwargs):
        return self.crequest(constants.OPTIONS, url, content, **kwargs)
        
    def chead(self, url, content: Content, **kwargs):
        return self.crequest(constants.HEAD, url, content, **kwargs)
        
    def cpatch(self, url, content: Content, **kwargs):
        return self.crequest(constants.PATCH, url, content, **kwargs)

    def download(self, method, url, content, save_as, **kwargs):
        raise NotImplementedError("Haven't been implemented yet")
