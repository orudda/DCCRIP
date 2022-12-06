
.PHONY: help run_cli run_rt


.DEFAULT: help
help:
	@echo "make run_cli"
	@echo "       run python3 cli_interface.py"
	@echo "make run_rt"
	@echo "       run python3 roteador.py $(arg1) $(arg2)"

run_cli:
	python3 cli_interface.py

run_rt:
	python3 roteador.py $(arg1) $(arg2)