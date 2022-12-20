# -*- coding: utf-8 -*-
from dotenv import find_dotenv, load_dotenv

from .local import Local
from .runtime import Runtime
from .test import Test
from .unit_test import UnitTest


try:
    load_dotenv(find_dotenv())
except Exception as e:
    print(f"Could not load {e}")
