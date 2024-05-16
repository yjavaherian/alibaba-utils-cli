import typer
from rich import print
import requests
from pathlib import Path
from typing import Any
from pydantic import BaseModel

# using types of the backend api
import _types


class Config(BaseModel):
    token:str=""
    base_url:str="http://localhost:8000"

# managing an external config file in users home directory.
class Store:
    config_dir = Path.home() / '.alibaba' 
    config_path = config_dir / 'config.json'
    config = Config()
    def __init__(self) -> None:
        if self.config_path.exists():
            self.config = Config.model_validate_json(self.config_path.read_text())
    
    def backup(self) -> None:
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as file:
            file.write(self.config.model_dump_json())
        
    

store = Store()
app = typer.Typer()

license_app = typer.Typer()
app.add_typer(license_app, name="license")

users_app = typer.Typer()
app.add_typer(users_app, name="users")

terminals_app = typer.Typer()
app.add_typer(terminals_app, name="terminals")


pipelines_app = typer.Typer()
app.add_typer(pipelines_app, name="pipelines")

tests_app = typer.Typer()
app.add_typer(tests_app, name="test")


def _request(
    method: str, endpoint: str, data: Any, model=None, auth: bool = False,data_as_form:bool = False
):
    args = {"method": method, "url": store.config.base_url + endpoint}
    if method == "get":
        args["params"] = data
    elif method == "post" or method == "put":
        args["json"] = data
    if auth and store.config.token:
        args["headers"] = {
            "Authorization": f"Bearer {store.config.token}",
            "Content-Type": "application/json",
        }
    if data_as_form:
        args["data"] = data
    try:
        res = requests.request(**args)
        res.raise_for_status()
        res = res.json()

        if type(res) == list:
            res = [model.model_validate(item) for item in res]
        else:
            res = model.model_validate(res)
        return res
    except Exception as e:
        print(e)
        return None
        
# ----------------------------------------- CLI Commands -------------------------------------------------
@license_app.command("create")
def create_license(value:str):
    license = _types.LicenseCreate.model_validate({"value":value})
    print(_request(
        "post", "/licenses/", license.model_dump(), _types.License, True
    ))

@license_app.command("list")
def get_licenses(skip: int = 0, limit: int = 100):
    print(_request(
        "get", "/licenses/", {"skip": skip, "limit": limit}, _types.License, True
    ))

@app.command("signup")
def sign_up(username:str,password:str,gotify_app_token:str,alibaba_username:str,alibaba_password:str,license:str):
    user = _types.UserCreate.model_validate({"username":username,"password":password,"gotify_app_token":gotify_app_token,"alibaba_username":alibaba_username,"alibaba_password":alibaba_password,"license":license})
    print(_request("post", "/users/", user.model_dump(), _types.User, False))

@app.command("me")
def info():
    print(_request("get", "/users/me/",{},_types.User, True))


@app.command("login")
def login(username: str, password: str):
    res = _request(
        "post",
        "/users/login/",
        {"username": username, "password": password},
        model=_types.Token,
        auth=False,
        data_as_form=True
    )
    store.config.token = res.access_token
    store.backup()
    

@terminals_app.command("list")
def get_terminals(skip: int = 0, limit: int = 100):
    print(_request(
        "get",
        "/terminals/",
        {"skip": skip, "limit": limit},
        _types.Terminal,
        False,
    ))

@terminals_app.command("create")
def add_terminal(id:int,name:str):
    terminal = _types.Terminal.model_validate({"id":id,"name":name})
    print(_request(
        "post", "/terminals/", terminal.model_dump(), _types.Terminal, True
    ))

@pipelines_app.command("delete")
def del_pipeline(id: int):
    print(_request("delete", f"/pipelines/{id}",{}, _types.Pipeline, True))

@pipelines_app.command("view")
def get_pipeline(id: int):
    print(_request("get", f"/pipelines/{id}",{}, _types.Pipeline, True))

@pipelines_app.command("list")
def get_pipelines():
    print(_request("get", "/pipelines",{}, _types.Pipeline, True))

@pipelines_app.command("create")
def add_pipeline(desc:str,date:str,origin_terminal:str,dest_terminal:str,start_time:str ="", end_time:str = ""):
    fields ={
        'desc':desc,
        'date':date,
        'origin_terminal':origin_terminal,
        'dest_terminal':dest_terminal,
    }
    if start_time != "" or end_time != "":
        fields['search_filter'] = {'start_time':start_time,'end_time':end_time}
    pipeline = _types.PipelineCreate.model_validate(fields)
    print(_request(
        "post", "/pipelines", fields, _types.Pipeline, True
    ))


@tests_app.command("gotify")
def test_gotify():
    print(_request("get", f"/test",{}, str, True))


if __name__ == "__main__":
    app()
