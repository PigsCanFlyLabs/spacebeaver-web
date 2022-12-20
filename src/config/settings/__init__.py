# -*- coding: utf-8 -*-
from .local import Local
from .runtime import Runtime
from .test import Test
from .unit_test import UnitTest
from dotenv import load_dotenv, find_dotenv

try:
    load_dotenv(find_dotenv())
except Exception as e:
    print(f"Could not load {e}")
