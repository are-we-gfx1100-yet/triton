#!/usr/bin/env bash

docker run \
  -ti \
  --ipc=host --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --device=/dev/kfd --device=/dev/dri --group-add video --shm-size 8G \
  -v .:/mnt/triton \
  -e HIP_VISIBLE_DEVICES=0 \
  -e HSA_OVERRIDE_GFX_VERSION=11.0.0 \
  triton-rocm:latest \
  bash
