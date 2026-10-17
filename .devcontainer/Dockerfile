FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

USER root

# La imagen base puede incluir un repositorio de Yarn cuya clave
# haya expirado o no esté disponible. El proyecto no utiliza Yarn,
# por lo que se elimina antes de instalar las Dev Container Features.
RUN rm -f \
    /etc/apt/sources.list.d/yarn.list \
    /etc/apt/sources.list.d/yarn.sources

USER vscode
DOCKERFILEcat > .devcontainer/Dockerfile <<'DOCKERFILE'
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

USER root

# La imagen base puede incluir un repositorio de Yarn cuya clave
# haya expirado o no esté disponible. El proyecto no utiliza Yarn,
# por lo que se elimina antes de instalar las Dev Container Features.
RUN rm -f \
    /etc/apt/sources.list.d/yarn.list \
    /etc/apt/sources.list.d/yarn.sources

USER vscode
