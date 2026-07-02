__version__ = "0.1.1"
__author__ = "Shashi Kundan"
__email__ = "shashikundan0001@gmail.com"

from uniconnect.core.factory import connect, get_connector
from uniconnect.core.registry import registry
from uniconnect.core.base import BaseConnector

import uniconnect.connectors  # noqa: F401, triggers auto-registration

__all__ = ["connect", "get_connector", "registry", "BaseConnector"]
