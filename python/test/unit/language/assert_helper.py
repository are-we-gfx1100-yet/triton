import sys

import torch
from torch.testing import assert_close

import triton
import triton.language as tl


@triton.jit
def kernel_device_assert(X, Y, BLOCK: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    tl.device_assert(x == 0, "x != 0")
    tl.store(Y + tl.arange(0, BLOCK), x)


@triton.jit
def kernel_device_assert_scalar(X, Y, BLOCK: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    # Trivial assert
    tl.device_assert(0 == 0, "x != 0")
    tl.store(Y + tl.arange(0, BLOCK), x)


@triton.jit(debug=False)
def kernel_device_assert_no_debug(X, Y, BLOCK: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    tl.device_assert(x == 0, "x != 0")
    tl.store(Y + tl.arange(0, BLOCK), x)


@triton.jit
def kernel_assert(X, Y, BLOCK: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    assert x == 0, "x != 0"
    tl.store(Y + tl.arange(0, BLOCK), x)


@triton.jit
def kernel_static_assert(X, Y, BLOCK: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    tl.static_assert(BLOCK == 128, "BLOCK != 128")
    tl.store(Y + tl.arange(0, BLOCK), x)


def test_assert(func: str):
    shape = (128, )
    x = torch.arange(0, shape[0], dtype=torch.int32, device='cuda')
    y = torch.zeros(shape, dtype=x.dtype, device="cuda")
    if func == "device_assert":
        kernel_device_assert[(1,)](x, y, num_warps=2, BLOCK=shape[0])
        kernel_device_assert_scalar[(1,)](x, y, num_warps=2, BLOCK=shape[0])
    elif func == "no_debug":
        # TRITON_DEBUG=True can override the debug flag
        kernel_device_assert_no_debug[(1,)](x, y, num_warps=2, BLOCK=shape[0])
    elif func == "assert":
        kernel_assert[(1,)](x, y, num_warps=2, BLOCK=shape[0])
    elif func == "static_assert":
        kernel_static_assert[(1,)](x, y, BLOCK=shape[0])
    assert_close(y, x)


@triton.jit
def jit_device_assert_none(x):
    tl.device_assert(x == 0, "x != 0")


@triton.jit(debug=True)
def jit_device_assert_true(x):
    tl.device_assert(x == 0, "x != 0")


@triton.jit(debug=False)
def jit_device_assert_false(x):
    tl.device_assert(x == 0, "x != 0")


@triton.jit
def kernel_device_assert_nested(X, Y, BLOCK: tl.constexpr, jit_debug: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    if jit_debug == "true":
        jit_device_assert_true(x)
    elif jit_debug == "false":
        jit_device_assert_false(x)
    else:
        jit_device_assert_none(x)
    tl.store(Y + tl.arange(0, BLOCK), x)


@triton.jit(debug=True)
def kernel_device_assert_nested_true(X, Y, BLOCK: tl.constexpr, jit_debug: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    if jit_debug == "true":
        jit_device_assert_true(x)
    elif jit_debug == "false":
        jit_device_assert_false(x)
    else:
        jit_device_assert_none(x)
    tl.store(Y + tl.arange(0, BLOCK), x)


@triton.jit(debug=False)
def kernel_device_assert_nested_false(X, Y, BLOCK: tl.constexpr, jit_debug: tl.constexpr):
    x = tl.load(X + tl.arange(0, BLOCK))
    if jit_debug == "true":
        jit_device_assert_true(x)
    elif jit_debug == "false":
        jit_device_assert_false(x)
    else:
        jit_device_assert_none(x)
    tl.store(Y + tl.arange(0, BLOCK), x)


def test_assert_nested(caller: str, callee: str):
    shape = (128, )
    x = torch.arange(0, shape[0], dtype=torch.int32, device='cuda')
    y = torch.zeros(shape, dtype=x.dtype, device="cuda")
    if caller == "none":
        kernel_device_assert_nested[(1,)](x, y, num_warps=2, BLOCK=shape[0], jit_debug=callee)
    elif caller == "true":
        kernel_device_assert_nested_true[(1,)](x, y, num_warps=2, BLOCK=shape[0], jit_debug=callee)
    elif caller == "false":
        kernel_device_assert_nested_false[(1,)](x, y, num_warps=2, BLOCK=shape[0], jit_debug=callee)
    assert_close(y, x)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        test_assert_nested(sys.argv[1], sys.argv[2])
    else:
        test_assert(sys.argv[1])
