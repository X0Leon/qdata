# -*- coding: utf-8 -*-

import yaml
from sqlalchemy import create_engine

with open("conf/config.yaml", "r") as f:
    config = yaml.load(f.read())["store"]

stock_db = create_engine(config["db_uri"], pool_size=16, max_overflow=0)