FROM ghcr.io/evshiron/rocm_lab:rocm5.5.1-ub22.04-base

USER root
WORKDIR /root

RUN apt install -y git wget vim python3-pip libpython3-dev
RUN pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm5.5

RUN pip3 install cmake lit pytest

ENV PATH="/root/.local/bin:$PATH"

ADD . triton
