import sys
import logging
import requests
import signal
import time

from environs import Env
from prometheus_client import start_http_server, Gauge, Counter

class Config:
    def __init__(self, api_url: str, scrape_interval: int, prom_port: int):
        self.prom_port = prom_port
        self.scrape_interval = scrape_interval
        self.api_url = api_url

class EnvConfigProvider:
    def __init__(self):
        env = Env()
        env.read_env()
        self.__env = env

    def get_config(self) -> Config:
        return Config(
            self.__env("ONCALL_API_URL"),
            self.__env.int("ONCALL_SCRAPE_INTERVAL"),
            self.__env.int("ONCALL_PROBER_PROMETHEUS_PORT"))

class Metrics:
    def __init__(self):
        self.__create_user_total = Counter(
            "oncall_prober_create_user_scenario_total","Total attempts to create user scenario"
        )
        self.__create_user_success = Counter(
            "oncall_prober_create_user_scenario_success", "Success attempts to create user scenario"
        )

    def add_create_user

class OncallProber:
    def __init__(self, config: Config, prom_wrapper):
        self.__config = config





