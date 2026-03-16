.PHONY: test-sourcing refresh-all

test-monitor:
	pytest tests/net_basis_monitor

test-sourcing:
	pytest tests/sourcing

refresh-portfolios:
	start "" "C:\Users\valentin\AppData\Local\Refinitiv\Refinitiv Workspace\RefinitivWorkspace.exe"
	python -m src.sourcing.application.refresh_all
