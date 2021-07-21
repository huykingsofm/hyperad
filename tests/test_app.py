import hyperad.app as browser
from hyperad.contents import (
    FieldContent, FileContent, JSONContent, MultiContent, ParamContent
)


def test_app():
    param = ParamContent("param1", "suboiz")
    print(param.build())

    field1 = FieldContent("field1", "ratatatata")
    print(field1.build())

    field2 = FieldContent("field2", "narutobaco")
    print(field2.build())

    field3 = FieldContent("field2", "sasuketamin")
    print(field3.build())

    file = FileContent("file", open("README.md", "rt"))
    print(file.build())

    json = JSONContent("file", {"luffee": "hancock", "sanjee": "namee"})
    print(json.build())

    form = MultiContent("form")
    form.add(param, field1, file, field3, json, field2)
    print(form.build())

    client = browser.App()
    resp = client.crequest("post", "http://localhost:8000/", form)
    print(resp)


if __name__ == "__main__":
    test_app()
