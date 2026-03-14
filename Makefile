.PHONY: test-sourcing refresh-all

test-sourcing:
	pytest tests/sourcing

refresh-portfolios:
	start "" "C:\Users\valentin\AppData\Local\Refinitiv\Refinitiv Workspace\RefinitivWorkspace.exe"
	python -m src.sourcing.application.refresh_all
