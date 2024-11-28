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
        self.__create_user_fail = Counter(
            "oncall_prober_create_user_scenario_fail", "Failed attempts to create user scenario"
        )
        self.__create_user_time = Gauge(
            "oncall_prober_create_user_scenario_time", "Time to run create user scenario"
        )

    def add_create_user_total(self) -> None:
        self.__create_user_total.inc()

    def add_create_user_success(self) -> None:
        self.__create_user_success.inc()

    def add_create_user_fail(self) -> None:
        self.__create_user_fail.inc()

    def set_create_user_time(self, duration: float) -> None:
        self.__create_user_time.set(duration)

class OncallProber:
    def __init__(self, config: Config, metrics: Metrics):
        self.__config = config
        self.__metrics = metrics

    def probe(self) -> None:
        metrics = self.__metrics
        api_url = self.__config.api_url

        metrics.add_create_user_total()
        logging.debug("try to run create user scenario")

        start = time.perf_counter()

        create_request = None
        delete_request = None
        username = 'test_prober_user'
        try:
            create_request = requests.post('%s/users' % api_url, json={
                "name": username
            })
        except Exception as err:
            logging.error(err)
            metrics.add_create_user_fail()
        finally:
            try:
                delete_request = requests.delete('%s/users/%s' % (api_url, username))
            except Exception as err:
                logging.error(err)

            if create_request and create_request.status_code == 200 and delete_request and delete_request.status_code == 200:
                metrics.add_create_user_success()
            else:
                metrics.add_create_user_fail()

            duration = time.perf_counter() - start
            metrics.set_create_user_time(duration)

def setup_logging():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s: %(message)s"
    )


def main():
    setup_logging()
    logging.debug("getting config")
    config = EnvConfigProvider().get_config()
    metrics = Metrics()
    prober = OncallProber(config, metrics)
    start_http_server(config.prom_port)

    while True:
        logging.debug("Run prober")
        prober.probe()
        logging.debug(f"Waiting {config.scrape_interval} before next probe")
        time.sleep(config.scrape_interval)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda signal_name, frame: sys.exit(0))
    main()