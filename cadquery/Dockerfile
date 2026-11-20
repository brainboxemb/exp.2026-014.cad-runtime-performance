ARG PYTHON_IMAGE=python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
FROM ${PYTHON_IMAGE} AS common

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libdbus-1-3 \
        libegl1 \
        libfontconfig1 \
        libglib2.0-0 \
        libgl1 \
        libice6 \
        libsm6 \
        libx11-6 \
        libx11-xcb1 \
        libxcb-cursor0 \
        libxcb-xinerama0 \
        libxcb1 \
        libxext6 \
        libxi6 \
        libxkbcommon-x11-0 \
        libxkbcommon0 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel
COPY scripts/cadquery_smoke.py /usr/local/bin/cadquery_smoke.py


FROM common AS full

RUN python -m pip install "cadquery==2.8.0"
RUN python /usr/local/bin/cadquery_smoke.py /tmp/full.stl


FROM common AS headless

RUN python -m pip install \
        "cadquery-ocp-novtk==7.9.3.1.1" \
        "ezdxf>=1.3.0" \
        "multimethod>=1.11,<2.0" \
        "nlopt>=2.9.0,<3.0" \
        runtype \
        casadi \
        "pyparsing>=3.0.0" \
        scipy \
        numba \
    && python -m pip install --no-deps "cadquery==2.8.0"

RUN python /usr/local/bin/cadquery_smoke.py /tmp/headless.stl
