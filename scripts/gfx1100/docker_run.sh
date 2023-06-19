#!/usr/bin/env bash

docker run \
  -ti \
  -v .:/mnt/triton \
  triton-rocm:latest \
  bash
