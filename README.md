# HYPERAD
A framework helps client applications communicate with web server via HTTP
protocol.

# REQUIREMENTS
+ Git
+ Python >= 3.7.1

# INSTALLATION
Clone the repository:
```shell
> git clone https://github.com/huykingsofm/hyperad.git
> cd hyperad
hyperad>
```
Create virtual environment
```shell
hyperad> python -m venv venv
hyperad> "venv/Scripts/activate"
(venv) hyperad>
```
Install library
```shell
(venv) hyperad $ pip install -e . 
```

# USAGE
All data that is submited to web server is represented by `Content` objects.  There are five `Content` classes, including:
+ `ParamContent`:  is used to send a name-value data as a parameters of url. E.g. https://some.url/?param1=value1.
+ `FieldContent`:  is used to send a name-value data inside the body of http request.  The body is under enctype (Content-Type) application/x-www-form-urlencoded.  The body example is field1=value1.
+ `FileContent`:  is helpful when sending a file to webserver.  It can detect some file's types and set it to Content-Type header.  It also sets Content-Disposition header to indicate the filename.
+ `JSONContent`:  represents a JSON data.  It set Content-Type header to application/json.
+ `MultiContent`: is a combination of above `Content`s.  `ParamContent` always appears on the url and doesn't affect to body of request.  If `MultiContent` includes only `FieldContent`, the body request will be under Content-Type application/x-www-form-urlencoded; otherwise, multipart/form-data.

These above `Content` objects will be send to the webserver by a `App` object.  This is a subclass of `requests.sessions.Session`.  It defines some new methods, one of them is `crequest(method, url, content, **kwargs)`.  This method send the `content` to the `url` under a speicific `method`.

# EXAMPLE
```python
from hyperad.app import App
from hyperad import contents

username = contents.ParamContent("usn", "admin")
password = contents.ParamContent("pwd", "root")
form = MultiContent("form")
form.add(username, password)

app = App()
resp = app.cget("http://some.example.url/", form)
print(resp)
```