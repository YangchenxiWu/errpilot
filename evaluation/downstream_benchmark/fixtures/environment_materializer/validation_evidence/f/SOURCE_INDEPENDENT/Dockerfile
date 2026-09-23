FROM --platform=linux/amd64 docker.io/library/python@sha256:ba23c4870854aa0718113e8765e7f46acbf141c6be1e66957ddcf130bd88d59d
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
COPY dependencies.txt /__materializer/dependencies.txt
RUN ["python","-m","pip","install","-r","/__materializer/dependencies.txt"]
RUN ["python","-m","pip","install","--no-index","nonexistent-synthetic-package-errpilot==0"]
