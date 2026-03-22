.PHONY: test-sourcing refresh-all

test-monitor:
	pytest tests/net_basis_monitor

test-sourcing:
	pytest tests/sourcing

refresh:
	python -m src.sourcing.application.refresh_all

run:
	python -m src.net_basis_monitor.application.run_monitor