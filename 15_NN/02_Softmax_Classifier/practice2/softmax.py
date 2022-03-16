import numpy as np
from random import shuffle


def softmax_loss_naive(W, X, y, reg):
  """
  Softmax (cross-entropy) loss function, naive implementation (with loops)

  Inputs have dimension D, there are C classes, and we operate on minibatches
  of N examples.

  Inputs:
  - W: A numpy array of shape (D, C) containing weights.
  - X: A numpy array of shape (N, D) containing a minibatch of data.
  - y: A numpy array of shape (N,) containing training labels; y[i] = c means
    that X[i] has label c, where 0 <= c < C.
    You might or might not want to transform it into one-hot form (not obligatory)
  - reg: (float) regularization strength

  Returns a tuple of:
  - loss as single float
  - gradient with respect to weights W; an array of same shape as W
  """
  # Initialize the loss and gradient to zero.
  loss = 0.0
  dW = np.zeros_like(W)

  # In this naive implementation we have a for loop over the N samples
  for i, x in enumerate(X):
    #############################################################################
    # TODO: Compute the cross-entropy loss using explicit loops and store the   #
    # sum of losses in "loss". If you already understand the process well       #
    # and are familiar with vectorized operations, you can solve this task      #
    # without inner loops and use vectorized operations instead.                #
    # PS! But in this case still keep the outer loop that enumerates over X!    #
    # If you are not careful in implementing softmax, it is easy to run into    #
    # numeric instability, because exp(a) is huge if a is large.                #
    # Read the Practical issues: numeric stability section from here:           #
    # https://cs231n.github.io/linear-classify/#softmax-classifier              #
    #############################################################################
    # TODO: use explicit loops or vectorized operations, either is ok!
    scores = X[i, :].dot(W)
    exp_scores = np.exp(scores)
    prob_scores = exp_scores/np.sum(exp_scores)
    #############################################################################
    # TODO: Compute the gradient using explicit loops and store the sum over    #
    # samples in dW. Again, you are allowed to use vectorized operations        #
    # if you know how to.                                                       #
    #############################################################################
    num_dims = W.shape[0]
    num_classes = W.shape[1]
    for d in range(num_dims):
      for k in range(num_classes):
        if k == y[i]:
          dW[d, k] += X.T[d, i] * (prob_scores[k]-1)
        else:
          dW[d, k] += X.T[d, i] * prob_scores[k]
    loss += -np.log(prob_scores[y[i]])
    #############################################################################
    #                          END OF YOUR CODE                                 #
    #############################################################################
  # now we turn the sum into an average by dividing with N
  loss /= X.shape[0]
  dW /= X.shape[0]

  # Add regularization to the loss and gradients.
  loss += reg * np.sum(W * W)
  dW += reg * 2 * W

  return loss, dW


def softmax_loss_vectorized(W, X, y, reg):
  """
  Softmax (cross-entropy) loss function, vectorized version.

  Inputs and outputs are the same as softmax_loss_naive.
  """
  # Initialize the loss and gradient to zero.
  loss = 0.0
  dW = np.zeros_like(W)

  #############################################################################
  # TODO: Compute the cross-entropy loss and its gradient using no loops.     #
  # Store the loss in loss and the gradient in dW.                            #
  # Make sure you take the average.                                           #
  # If you are not careful with softmax, you migh run into numeric instability#
  #############################################################################
  num_train = X.shape[0]

  scores = np.dot(X, W)
  exp_scores = np.exp(scores)
  prob_scores = exp_scores/np.sum(exp_scores, axis=1, keepdims=True)
  correct_log_probs = -np.log(prob_scores[range(num_train), y])
  
  loss = np.sum(correct_log_probs)
  loss /= num_train
  dscores = prob_scores
  dscores[range(num_train), y] -= 1
  dW = np.dot(X.T, dscores)
  dW /= num_train
  #############################################################################
  #                          END OF YOUR CODE                                 #
  #############################################################################

  # Add regularization to the loss and gradients.
  loss += reg * np.sum(W * W)
  dW += reg * 2 * W

  return loss, dW
