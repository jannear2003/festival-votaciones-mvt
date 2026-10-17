FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

USER root

# La imagen base puede incluir un repositorio de Yarn cuya clave
# no este disponible. El proyecto no utiliza Yarn, por lo que se
# elimina esa fuente antes de instalar las Dev Container Features.
RUN rm -f \
    /etc/apt/sources.list.d/yarn.list \
    /etc/apt/sources.list.d/yarn.sources

USER vscode
