FROM --platform=linux/amd64 docker.io/library/python@sha256:1d24b4656d4df536d8fa690be572774aa84b56c0418266b73886dc8138f047e6
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY dependencies.txt /__materializer/dependencies.txt
RUN ["python","-m","pip","install","-r","/__materializer/dependencies.txt"]
