import glob
import os
import socket
import uuid
from typing import TYPE_CHECKING, Iterator, Tuple

import pytest

from imap_tools import MailBoxUnencrypted

if TYPE_CHECKING:
    from pytest_docker.plugin import Services

MESSAGES_DIR = os.path.join(os.path.dirname(__file__), "messages")


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: pytest.Config) -> str:
    return os.path.join(str(pytestconfig.rootdir), "tests", "docker-compose.yml")


@pytest.fixture(scope="session")
def greenmail_service(docker_ip: str, docker_services: "Services") -> Tuple[str, int]:
    port = docker_services.port_for("greenmail", 3143)

    def is_responsive() -> bool:
        try:
            with socket.create_connection((docker_ip, port), timeout=1):
                return True
        except OSError:
            return False

    docker_services.wait_until_responsive(timeout=30.0, pause=0.5, check=is_responsive)
    return docker_ip, port


@pytest.fixture
def greenmail_mailbox(greenmail_service: Tuple[str, int]) -> Iterator[MailBoxUnencrypted]:
    host, port = greenmail_service
    username = f"test-{uuid.uuid4().hex}@localhost"
    mailbox = MailBoxUnencrypted(host, port)
    mailbox.login(username, "password")
    for eml_path in sorted(glob.glob(os.path.join(MESSAGES_DIR, "*.eml"))):
        with open(eml_path, "rb") as f:
            mailbox.append(f.read(), folder="INBOX")
    mailbox.folder.set("INBOX")
    yield mailbox
    mailbox.logout()
