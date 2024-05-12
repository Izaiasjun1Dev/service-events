
# comandos para o dia a dia de desenvolvimento

# cores
RED=\033[0;31m
GREEN=\033[0;32m
NC=\033[0m # No Color
YELLOW=\033[0;33m

# funação para criar o arquivo de env
define create_env_local
	@echo "${YELLOW}criando arquivo de env 🏂${NC}"
	@cat devtools/envs/local.txt > .env
	@echo "${GREEN}Variaveis setadas! 👌${NC}"
endef

define create_env_test
	@echo "${YELLOW}criando arquivo de env 🏂${NC}"
	@cat devtools/envs/test.txt > .env
	@echo "${GREEN}Variaveis setadas! 👌${NC}"
endef



define clean
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "*.log" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@find . -name ".pytest_cache" -type d | xargs rm -rf
endef


clear:
	@clear
	$(call clean)


build-local:
	@clear
	@pipenv uninstall judici
	@pipenv install .

