#!/usr/bin/env bash

docker build \
  -f scripts/gfx1100/Dockerfile \
  -t triton-rocm:latest \
  .
