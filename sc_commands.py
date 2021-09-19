from scrapli.driver.core import IOSXRDriver
import logging
from typing import Dict, List, Union
from list_routers import router_1, router_2, router_1_config, router_2_config

LOGGER = logging.getLogger(__name__)
logging.getLogger("scrapli").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


class Router_l2vpn:
    def __init__(
        self,
        router_1: Dict[str, Union[str, int, bool]],
        router_1_config: List[str],
        router_2: Dict[str, Union[str, int, bool]],
        router_2_config: List[str],
    ) -> None:
        """
        :attr router_1: dictionary of a router configuration
        :attr router_1_config: configuration list
        :attr router_2: dictionary of a router configuration
        :attr router_2_config: configuration list
        """
        self.router_1 = router_1
        self.router_1_config = router_1_config
        self.router_2 = router_2
        self.router_2_config = router_2_config
        self._clean_interfaces(
            self.router_1, self.router_1_config, self.router_2, self.router_2_config
        )
        self._configure_interfaces(
            self.router_1, self.router_1_config, self.router_2, self.router_2_config
        )
        self._clean_xconnects(
            self.router_1, self.router_1_config, self.router_2, self.router_2_config
        )

        self._configuration_l2vpns(
            router_1, router_1_config, router_2, router_2_config
        )

    def _open_connection(self, router: Dict[str, Union[str, int, bool]]):
        """
        return: Scrapli connection
        """

        return IOSXRDriver(**router)

    def _clean_interfaces(
        self,
        router_1: Dict[str, Union[str, int, bool]],
        router_1_config: List[str],
        router_2: Dict[str, Union[str, int, bool]],
        router_2_config: List[str],
    ):
        """
        :attr router_1: dictionary of a router configuration
        :attr router_1_config: configuration list
        :attr router_2: dictionary of a router configuration
        :attr router_2_config: configuration list
        return: None
        """

        self._clean_interface(router_1, router_1_config)
        self._clean_interface(router_2, router_2_config)

    def _clean_interface(
        self, router: Dict[str, Union[str, int, bool]], router_config: List[str]
    ):
        """
        :attr router: dictionary of a router configuration
        :attr router_config: configuration list
        return: None
        """
        ssh = self._open_connection(router)
        ssh.open()
        result = ssh.send_command("sho running-config")

        if f"{router_config[1]}.{router_config[2]}" in result.result:

            LOGGER.info(f"{router_config[1]}.{router_config[2]} will be deleted")

            ssh.send_configs(
                [f"no interface {router_config[1]}.{router_config[2]}", "commit"]
            )
            result = ssh.send_command("sho running-config")

            if f"{router_config[1]}.{router_config[2]}" in result.result:
                LOGGER.info(
                    f"Interface {router_config[1]}.{router_config[2]} was not be deleted"
                )
            else:

                LOGGER.info(
                    f"Interface {router_config[1]}.{router_config[2]} was deleted"
                )
        else:
            LOGGER.info(
                f"{router_config[1]}.{router_config[2]} is not int the configuration"
            )
        ssh.close()

    def _clean_xconnects(
        self,
        router_1: Dict[str, Union[str, int, bool]],
        router_1_config: List[str],
        router_2: Dict[str, Union[str, int, bool]],
        router_2_config: List[str],
    ):
        """
        :attr router_1: dictionary of a router configuration
        :attr router_1_config: configuration list
        :attr router_2: dictionary of a router configuration
        :attr router_2_config: configuration list
        return: None
        """
        self._clean_xconnect(router_1, router_1_config)
        self._clean_xconnect(router_2, router_2_config)

    def _clean_xconnect(
        self, router: Dict[str, Union[str, int, bool]], router_config: List[str]
    ):
        """
        :attr router: dictionary of a router configuration
        :attr router_config: configuration list
        return: None
        """
        logging.info(f"Checking l2vpn xconnect {router_config[2]}")

        ssh = self._open_connection(router)
        ssh.open()
        result = ssh.send_command("show running-config")

        if f"xconnect group {router_config[2]}" in result.result:
            LOGGER.info(f"xconnect group {router_config[2]} will be deleted")
            ssh.send_configs(
                ["l2vpn", f" no xconnect group {router_config[2]}", "commit"]
            )
            result = ssh.send_command("show running-config")

            if f"xconnect group test {router_config[2]}" in result.result:
                LOGGER.info(f"xconnect group {router_config[2]} was not be deleted")
            else:
                LOGGER.info(f"xconnect group {router_config[2]} was deleted")
        else:
            LOGGER.info(
                f"xconnect group {router_config[2]} is not int the configuration"
            )
        ssh.close()

    def _configure_interfaces(
        self,
        router_1: Dict[str, Union[str, int, bool]],
        router_1_config: List[str],
        router_2: Dict[str, Union[str, int, bool]],
        router_2_config: List[str],
    ):
        """
        :attr router_1: dictionary of a router configuration
        :attr router_1_config: configuration list
        :attr router_2: dictionary of a router configuration
        :attr router_2_config: configuration list
        return: None
        """

        self._configure_interface(router_1, router_1_config)
        self._configure_interface(router_2, router_2_config)

    def _configure_interface(
        self, router: Dict[str, Union[str, int, bool]], router_config: str
    ):
        """
        :attr router: dictionary of a router configuration
        :attr router_config: configuration list
        return: None
        """

        ssh = self._open_connection(router)
        ssh.open()
        results = ssh.send_configs(
            [
                f"interface {router_config[1]}.{router_config[2]} l2transport",
                f"encapsulation dot1q {router_config[2]}",
                "commit",
            ],
            strip_prompt=False,
        )

        ssh.close()
        LOGGER.info(f"Interface {router_config[1]}.{router_config[2]} was created")

    def _configuration_l2vpns(
        self,
        router_1: Dict[str, Union[str, int, bool]],
        router_1_config: str,
        router_2: Dict[str, Union[str, int, bool]],
        router_2_config: str,
    ):
        """
        :attr router_1: dictionary of a router configuration
        :attr router_1_config: configuration list
        :attr router_2: dictionary of a router configuration
        :attr router_2_config: configuration list
        return: None
        """

        self._configure_l2vpn(router_1, router_1_config, router_2_config)
        self._configure_l2vpn(router_2, router_2_config, router_1_config)
        return None

    def _configure_l2vpn(
        self,
        router: Dict[str, Union[str, int, bool]],
        router_config_main: List[str],
        router_config_secondary: List[str],
    ):
        """
        :attr router: dictionary of a router configuration
        :attr router_config_main: Main configuration list
        :attr router_config_secondary: Secondary configuration list
        return: None
        """

        ssh = self._open_connection(router)
        ssh.open()
        results = ssh.send_configs(
            [
                "l2vpn",
                f"xconnect group {router_config_main[2]}",
                f"p2p {router_config_main[2]}",
                f"interface {router_config_main[1]}.{router_config_main[2]}",
                f"neighbor ipv4 {router_config_secondary[0]} pw-id 200",
                "commit",
            ],
            strip_prompt=False,
        )

        ssh.close()
        LOGGER.info(f"L2vpn xconnect {router_config_main[2]} was created")

if __name__ == "__main__":
    r = Router_l2vpn(router_1, router_1_config, router_2, router_2_config)
