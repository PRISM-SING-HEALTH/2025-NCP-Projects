import os
import json
import sys
import yaml
import pronto
import streamlit as st
import pandas as pd
import streamlit.web.cli as stcli


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app_main.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())
    