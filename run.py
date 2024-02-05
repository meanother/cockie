#!/root/code/cookie/env/bin/python

import requests
import subprocess

from pathlib import Path
from loguru import logger

# path: /Users/arty/code/cockie/config.js
config_path = "/root/WgEasyServer/config.js"

log_dir = Path.home().joinpath("logs")
log_dir.mkdir(parents=True, exist_ok=True)

logger.add(
    log_dir.joinpath("cookie-refresher.log"),
    format="{time} [{level}] {module} {name} {function} - {message}",
    level="DEBUG",
    compression="zip",
    rotation="30 MB",
)


def read_config() -> dict:
    path = Path(config_path)
    if not path.exists():
        logger.error("file: config.js not found!")
        return {}
    with open(path, "r") as f:
        file = f.read().split("\n")

    for line in file:
        print(line)

    password = file[1].split(" = ")[1].replace('"', '')[:-1]
    cookie = file[3].split(" = ")[1].replace('"', '')[:-1]
    url = file[2].split(" = ")[1].replace('"', '')[:-1]

    return {
        "password": password,
        "cookie": cookie,
        "url": url,
    }


def replace(old_value: str, new_value: str) -> None:
    path = Path(config_path)
    if not path.exists():
        logger.error("file: config.js not found!")

    with open(path, "r") as f:
        file = f.read()

    with open(path, "w") as f:
        new_data = file.replace(old_value, new_value)
        f.write(new_data)

    logger.info(f"Replace cookie: {old_value} --> {new_value} success!")


def replace_new_cookie() -> None:
    config = read_config()
    logger.info(f"config: {config}")
    session = requests.Session()
    data = {"password": config["password"]}
    request = session.post(f"{config['url']}/api/session", json=data)
    logger.info(f"status code: {request.status_code}")

    cookies = request.cookies
    cookies_dict = requests.utils.dict_from_cookiejar(cookies)  # noqa

    new_cookie = cookies_dict["connect.sid"]
    logger.info(f"new cookie: {new_cookie}")

    replace(config["cookie"], f"connect.sid={new_cookie}")


def restart_pm2() -> None:
    cmd = ["pm2", "restart", "WgEasyServer/index.js"]
    result = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode("utf-8")
    logger.info(result)


replace_new_cookie()
restart_pm2()
