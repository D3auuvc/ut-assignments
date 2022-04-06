from builtins import range
import numpy as np

'''

def im2col_indices(x, field_height, field_width, padding=1, stride=1):
  """ An implementation of im2col based on some fancy indexing """
  # Zero-pad the input
  p = padding
  x_padded = np.pad(x, ((0, 0), (0, 0), (p, p), (p, p)), mode='constant')

  k, i, j = get_im2col_indices(x.shape, field_height, field_width, padding,
                               stride)

  cols = x_padded[:, k, i, j]
  C = x.shape[1]
  cols = cols.transpose(1, 2, 0).reshape(field_height * field_width * C, -1)
  return cols


def get_im2col_indices(x_shape, field_height, field_width, padding=1, stride=1):
  # First figure out what the size of the output should be
  N, C, H, W = x_shape
  assert (H + 2 * padding - field_height) % stride == 0
  assert (W + 2 * padding - field_height) % stride == 0
  out_height = (H + 2 * padding - field_height) / stride + 1
  out_width = (W + 2 * padding - field_width) / stride + 1

  i0 = np.repeat(np.arange(field_height), field_width))
  i0 = np.tile(i0, C)
  i1 = stride * np.repeat(np.arange(out_height), out_width)
  j0 = np.tile(np.arange(field_width), field_height * C)
  j1 = stride * np.tile(np.arange(out_width), out_height)
  i = i0.reshape(-1, 1) + i1.reshape(1, -1)
  j = j0.reshape(-1, 1) + j1.reshape(1, -1)

  k = int(np.repeat(np.arange(C), field_height * field_width).reshape(-1, 1))

  return (k, i, j)


'''


def conv_forward_naive(x, w, b, conv_param):
    """
    A naive implementation of the forward pass for a convolutional layer.

    The input consists of N data points, each with C channels, height H and
    width W. We convolve each input with F different filters, where each filter
    spans all C channels and has height HH and width HH.

    Input:
    - x: Input data of shape (N, C, H, W)
    - w: Filter weights of shape (F, C, HH, WW)
    - b: Biases, of shape (F,)
    - conv_param: A dictionary with the following keys:
      - 'stride': The number of pixels between adjacent receptive fields in the
        horizontal and vertical directions.
      - 'pad': The number of pixels that will be used to zero-pad the input.

    Returns a tuple of:
    - out: Output data, of shape (N, F, H', W') where H' and W' are given by
      H' = 1 + (H + 2 * pad - HH) / stride
      W' = 1 + (W + 2 * pad - WW) / stride
    - cache: (x, w, b, conv_param)
    """
    out = None
    ###########################################################################
    # TODO: Implement the convolutional forward pass.                         #
    # Hint: you can use the function np.pad for padding.                      #
    ###########################################################################
    pad, stride = conv_param['pad'], conv_param['stride']
    N, C, H, W = x.shape
    F, C, HH, WW = w.shape
    H_ = 1 + (H + 2 * pad - HH) // stride
    W_ = 1 + (W + 2 * pad - WW) // stride

    out = np.zeros((N, F, H_, W_))
    x_padded = np.pad(x, ((0,), (0,), (pad,), (pad,)), 'constant')
    w_reshaped = w.reshape(F, -1).T

    for i, ii in enumerate(range(0, H_*stride, stride)):
        for j, jj in enumerate(range(0, W_*stride, stride)):
            out[:, :, i, j] = np.dot(
                x_padded[:, :, ii:ii+HH, jj:jj+WW].reshape(N, -1), w_reshaped) + b

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    cache = (x, w, b, conv_param)
    return out, cache


def conv_backward_naive(dout, cache):
    """
    A naive implementation of the backward pass for a convolutional layer.

    Inputs:
    - dout: Upstream derivatives.
    - cache: A tuple of (x, w, b, conv_param) as in conv_forward_naive

    Returns a tuple of:
    - dx: Gradient with respect to x
    - dw: Gradient with respect to w
    - db: Gradient with respect to b
    """
    dx, dw, db = None, None, None
    ###########################################################################
    # TODO: Implement the convolutional backward pass.                        #
    ###########################################################################
    x, w, b, conv_param = cache
    pad, stride = conv_param['pad'], conv_param['stride']
    x_padded = np.pad(x, ((0,), (0,), (pad,), (pad,)), 'constant')

    N, C, H, W = x.shape
    F, C, HH, WW = w.shape
    _, _, H_, W_ = dout.shape

    dx_padded, dw = np.zeros(x_padded.shape), np.zeros(w.shape)
    w_reshaped = w.reshape(F, -1)

    for i, ii in enumerate(range(0, H_*stride, stride)):
        for j, jj in enumerate(range(0, W_*stride, stride)):
            dw += np.dot(dout[:, :, i, j].T, x_padded[:, :, ii:ii +
                         HH, jj:jj+WW].reshape(N, -1)).reshape(dw.shape)
            dx_padded[:, :, ii:ii+HH, jj:jj +
                      WW] += np.dot(dout[:, :, i, j], w_reshaped).reshape(N, C, HH, WW)
    dx = dx_padded[:, :, pad:-pad, pad:-pad]
    db = np.sum(dout, axis=(0, 2, 3))
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return dx, dw, db


def max_pool_forward_naive(x, pool_param):
    """
    A naive implementation of the forward pass for a max pooling layer.

    Inputs:
    - x: Input data, of shape (N, C, H, W)
    - pool_param: dictionary with the following keys:
      - 'pool_height': The height of each pooling region
      - 'pool_width': The width of each pooling region
      - 'stride': The distance between adjacent pooling regions

    Returns a tuple of:
    - out: Output data
    - cache: (x, pool_param)
    """
    out = None
    ###########################################################################
    # TODO: Implement the max pooling forward pass                            #
    ###########################################################################
    # Extract shapes and constants
    N, C, H, W = x.shape
    HH = pool_param.get('pool_height', 2)
    WW = pool_param.get('pool_width', 2)
    stride = pool_param.get('stride', 2)
    assert (H - HH) % stride == 0, 'Sanity Check Status: Max Pool Failed in Height'
    assert (W - WW) % stride == 0, 'Sanity Check Status: Max Pool Failed in Width'
    H_prime = 1 + (H - HH) // stride
    W_prime = 1 + (W - WW) // stride
    # Construct output
    out = np.zeros((N, C, H_prime, W_prime))
    # Naive Loops
    for n in range(N):
        for j in range(H_prime):
            for i in range(W_prime):
                out[n, :, j, i] = np.amax(
                    x[n, :, j*stride:j*stride+HH, i*stride:i*stride+WW], axis=(-1, -2))

    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    cache = (x, pool_param)
    return out, cache


def max_pool_backward_naive(dout, cache):
    """
    A naive implementation of the backward pass for a max pooling layer.

    Inputs:
    - dout: Upstream derivatives
    - cache: A tuple of (x, pool_param) as in the forward pass.

    Returns:
    - dx: Gradient with respect to x
    """
    dx = None
    ###########################################################################
    # TODO: Implement the max pooling backward pass                           #
    ###########################################################################
    # Extract constants and shapes
    x, pool_param = cache
    N, C, H, W = x.shape
    HH = pool_param.get('pool_height', 2)
    WW = pool_param.get('pool_width', 2)
    stride = pool_param.get('stride', 2)
    H_prime = 1 + (H - HH) // stride
    W_prime = 1 + (W - WW) // stride
    # Construct output
    dx = np.zeros_like(x)
    # Naive Loops
    for n in range(N):
        for c in range(C):
            for j in range(H_prime):
                for i in range(W_prime):
                    ind = np.argmax(
                        x[n, c, j*stride:j*stride+HH, i*stride:i*stride+WW])
                    ind1, ind2 = np.unravel_index(ind, (HH, WW))
                    dx[n, c, j*stride:j*stride+HH, i*stride:i *
                        stride+WW][ind1, ind2] = dout[n, c, j, i]
    ###########################################################################
    #                             END OF YOUR CODE                            #
    ###########################################################################
    return dx
