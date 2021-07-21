import io
import os
import abc
import mimetypes
from json import dumps as jsondumps
from typing import Any, Dict, Iterable, List, Optional, Union

from hyperad.constants import (
    CONTENT_TYPE, CONTENT_DISPOSITION,
    APPLICATION_JSON, MULTIPART_FORM_DATA, TEXT_PLAIN,
    APPLICATION_X_WWW_FORM_URLENCODED, APPLICATION_OCTET_STREAM,
)
from hyperad.errors import DuplicateValue


_REQUEST_PARAMS = Dict


class Content(abc.ABC):
    """ The abstract base class for a content submited to the web server.
    @param `name`: Name of `Content`.  It can be a `str` or `bytes` object.
    """
    def __init__(self, name: Union[str, bytes]) -> None:
        super().__init__()
        if not isinstance(name, (str, bytes)):
            raise TypeError("name is expected as a str or bytes object")

        self._name = name
    
    @abc.abstractmethod
    def _build(self) -> _REQUEST_PARAMS:
        """ Construct the paramters that are passed into `requests.request()`
        method.
        """
        pass

    def build(self) -> _REQUEST_PARAMS:
        return self._build()


    @abc.abstractmethod
    def enctype(self) -> str:
        """ Return the Content-Type of this `Content`.
        """
        pass

    def name(self) -> str:
        """ Return name of `Content`.
        """
        return self._name


class ParamContent(Content):
    """ A simple `Content` represents a NAME-VALUE data and is sent as a
    parameter in url.
    @param `name`: Name of `Content`.
    @param `value`: Value data.  It can be `str` or `bytes` object.
    """ 
    def __init__(self,
            name: Union[str, bytes],
            value: Union[str, bytes]
            ) -> None:
        super().__init__(name)

        if not isinstance(value, (str, bytes)):
            raise TypeError("value is expected as a byte-like object")

        self._value = value

    def _build(self) -> _REQUEST_PARAMS:
        return {
            "params": {self._name: self._value}
        }

    def enctype(self) -> str:
        # Because it is sent in the url, there is no type of this Content
        return None


class FieldContent(Content):
    """ A simple `Content` represents a NAME-VALUE data and is sent inside the
    body.
    @param `name`: Name of `Content`.
    @param `value`: Value data.  It can be `str` or `bytes` object.
    """
    def __init__(self,
            name: Union[str, bytes],
            value: Union[str, bytes]
            ) -> None:
        super().__init__(name)

        if not isinstance(value, (str, bytes)):
            raise TypeError("value is expected as a byte-like object")

        self._value = value

    def _build(self) -> _REQUEST_PARAMS:
        return {
            "data": {self._name: self._value}
        }

    def enctype(self) -> str:
        # Content-Type of `Field` is always "application/x-www-form-urlencoded"
        return APPLICATION_X_WWW_FORM_URLENCODED


class FileContent(Content):
    """ A `Content` supports to upload file.  The file could be a `bytes`,
    `str`, `io`, or `iterable` object.  The filename need to be indicated
    explicitly if the file is not `io` object.
    @param `name`: Name of `Content`.
    @param `file`: A `bytes` or `io` or `str` or `iterable` object\
        representing the file uploaded to the web server.
    @param `filename`: (Optional) Name of file. It is neccessary if\
        file doesn't have `name` attribute.   
    """
    def __init__(self,
            name: str,
            file: Union[str, bytes, io.IOBase, Iterable],
            filename: Optional[str] = None
            ) -> None:
        super().__init__(name)

        is_file = any([
            isinstance(file, (str, bytes)),
            isinstance(file, io.IOBase),
            hasattr(file, "__iter__")
        ])

        if not is_file:
            raise TypeError("file is expected as a file-like object or "
            "byte-like or iterable or str object")

        # Get filename if the filename parameter hasn't been passed and the 
        # file object provides one.
        if filename is None and hasattr(file, "name"):
            if callable(file.name):
                filename = file.name()
            else:
                filename = file.name

        if filename is None:
            raise ValueError("Please provide filename explicitly if "
            "file doesn't have name attribute")

        # Remove redundant path in filename
        self._filename = os.path.split(filename)[1]

        # Guess the Content-Type of the file relying on filename.  If it can't,
        # the default value will be set.
        self._enctype = mimetypes.guess_type(filename)[0]
        if self._enctype is None:
            if isinstance(file, (io.TextIOBase, str)):
                self._enctype = TEXT_PLAIN
            else:
                self._enctype = APPLICATION_OCTET_STREAM

        self._file = file

    def enctype(self):
        return self._enctype

    def filename(self):
        return self._filename

    def _build(self) -> Dict:
        """ The file will be sent in the HTTP request body.  This method
        specifies two headers, which are Content-Type and Content-Disposition.
        They can be received and processed at the server.
        """
        return {
            "data": self._file,
            "headers": {
                CONTENT_TYPE: self.enctype(),
                CONTENT_DISPOSITION: "attachment; filename={}"
                    .format(self._filename),
            }
        }


class JSONContent(Content):
    """ A `Content` helps send JSON to webserver.
    @param `name`: Name of `Content`.
    @param `json`: A serializable JSON object, such as `dict`.
    """
    def __init__(self, name: str, json: Any) -> None:
        super().__init__(name)

        try:
            jsondumps(json, allow_nan=False)
        except ValueError:
            raise ValueError("json is expected a serializable json "
            "object")

        self._json = json

    def _build(self) -> Dict:
        return {
            "json": self._json
        }

    def enctype(self) -> str:
        # The Content-Type of a JSON value is always "application/json".
        return APPLICATION_JSON


def _extract(d: Dict):
    if len(d.keys()) != 1:
        raise ValueError(
            "Only one-element dict can be extracted, "
            "{} element(s) found.".format(len(d.keys()))
        )

    key = list(d.keys())[0]
    value = d[key]

    return key, value


def _create_or_append(d: Dict, k: Any, v: Any):
    if k not in d.keys():
        d.update({k: [v]})
    else:
        d[k].append(v)


def _create_or_raise(d: Dict, k: Any, v: Any):
    if k in d.keys():
        raise DuplicateValue("Duplicated key ({})".format(k))

    d.update({k: v})


def _exact_is_instance(__obj, __class_or_tuple):
    if not hasattr(__class_or_tuple, "__iter__"):
        __class_or_tuple = (__class_or_tuple, )

    if not isinstance(__obj, __class_or_tuple):
        return False

    for cls in __class_or_tuple:
        if type(__obj) == cls:
            return True

    return False


class MultiContent(Content):
    """ A `Content` send data as multipart/form-data.
    @param name: Name of `Content`.
    """
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._content_list: List[Content] = []
        self._enctype = APPLICATION_X_WWW_FORM_URLENCODED

    def add(self, *contents: Content):
        """ Add `Content`s to the `MultiContent` form.
        - `Param` always appears in url path.
        - Other `Content`s will be put inside the body of request.

        @param `contents`: One or many `Content`s.
        """
        for content in contents:
            if not _exact_is_instance(content, (
                        ParamContent, FieldContent, FileContent, JSONContent
                    )):
                raise TypeError(
                    "Unsupported Content ({})"
                    .format(type(content).__name__)
                )

            if not isinstance(content, (FieldContent, ParamContent)):
                self._enctype = MULTIPART_FORM_DATA

            self._content_list.append(content)

        return None

    def _build(self) -> Dict:
        parameters = {"params": {}, "data": {}, "files": {}}

        for content in self._content_list:
            if isinstance(content, ParamContent):
                name, value = _extract(content.build()["params"])
                _create_or_append(parameters["params"], name, value)

            if isinstance(content, FieldContent):
                name, value = _extract(content.build()["data"])
                _create_or_append(parameters["data"], name, value)

            if isinstance(content, FileContent):
                name = content.name()
                file = content.build()["data"]
                enctype = content.enctype()
                filename = content.filename()

                value = (filename, file, enctype)
                _create_or_raise(parameters["files"], name, value)

            if isinstance(content, JSONContent):
                name = content.name()
                json = jsondumps(content.build()["json"])
                value = (None, json, APPLICATION_JSON)
                _create_or_raise(parameters["files"], name, value)

        return parameters

    def enctype(self) -> str:
        return self._enctype
