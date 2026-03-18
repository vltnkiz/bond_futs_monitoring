import logging
from typing import List

from src.net_basis_monitor.core.models.value_objects.monitoring_request import MonitoringRequest
from src.net_basis_monitor.core.ports.static_data_provider import StaticDataProvider

logger = logging.getLogger(__name__)


class MonitoringRequestBuilder:
    def __init__(self, static_data_provider: StaticDataProvider):
        self._static_data_provider = static_data_provider

    def build(self, future_ids: List[str]) -> List[MonitoringRequest]:
        all_futures = self._static_data_provider.get_futures()
        futures = [f for f in all_futures if f.contract_symbol in future_ids]

        if not futures:
            logger.warning("No futures found for the provided contract symbols.")
            return []

        requests = []
        for future in futures:
            if not future.deliverable_bonds:
                logger.warning(
                    f"Future {future.contract_symbol} has no deliverable bonds. Skipping."
                )
                continue

            for bond_id in future.deliverable_bonds:
                requests.append(
                    MonitoringRequest(
                        future_id=future.contract_symbol,
                        bond_id=bond_id,
                    )
                )

        return requests