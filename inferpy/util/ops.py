import numpy as np
import inferpy.models
import tensorflow as tf
import collections
import six



def get_total_dimension(x):

    D = 0

    if np.ndim(x) == 0:
        x = [x]

    for xi in x:
        if np.isscalar(xi):
            D = D + 1
        elif isinstance(xi, inferpy.models.RandomVariable):
            D = D + xi.dim
        elif isinstance(xi, tf.Tensor):
            D = D + xi.get_shape().as_list()[-1]

        else:
            raise ValueError("Wrong input type")


    return D




def param_to_tf(x):
    if np.isscalar(x):
        return tf.constant(x, dtype="float32")
    elif isinstance(x, inferpy.models.RandomVariable):
        return x.base_object
    else:
        raise ValueError("wrong input value in param_to_tf")


def ndim(v):
    if np.isscalar(v):
        return 0
    if not isinstance(v, collections.Iterable):
        v = [v]

    out = [1 if np.isscalar(x)
                  else (ndim(x) + 1 if type(x) in [np.ndarray, list]
                        else ndim(x.sample(1)[0]))
                  for x in v]
    return np.max(out)



def case_states(var, d, default=None, exclusive=True, strict=False, name='case'):
    out_d = {}

    if not isinstance(var, inferpy.models.RandomVariable):
        var = inferpy.models.Deterministic(var)


    def f(p): return tf.constant(p)


    for s, p in six.iteritems(d):

        out_d.update({tf.reduce_all(tf.equal(var.dist, tf.constant(s))): (lambda pp : lambda: f(pp))(p)})

    return tf.case(out_d, default=default, exclusive=exclusive,strict=strict,name=name)



def case(d, default=None, exclusive=True, strict=False, name='case'):
    out_d = {}


    def f(p): return tf.constant(p)

    for c, p in six.iteritems(d):

        out_d.update({tf.reduce_all(tf.equal(c.base_object, True)): (lambda pp : lambda: f(pp))(p)})


    if default != None:
        default = (lambda pp : lambda: f(pp))(default)

    return tf.case(out_d, default=default, exclusive=exclusive,strict=strict,name=name)



def gather(
        params,
        indices,
        validate_indices=None,
        name=None,
        axis=0 ):

    tf_params = params.base_object if isinstance(params, inferpy.models.RandomVariable)==True else params
    tf_indices = indices.base_object if isinstance(indices, inferpy.models.RandomVariable) == True else indices

    return  tf.gather(tf_params, tf_indices, validate_indices, name, axis)


def matmul(
        a,
        b,
        transpose_a=False,
        transpose_b=False,
        adjoint_a=False,
        adjoint_b=False,
        a_is_sparse=False,
        b_is_sparse=False,
        name=None):

    res = inferpy.models.Deterministic()


    a_shape = shape_to_list(a)
    b_shape = shape_to_list(b)


    if isinstance(a, inferpy.models.RandomVariable):
        a = a.base_object

    if isinstance(b, inferpy.models.RandomVariable):
        b = b.base_object


    a = a if len(a_shape) > 1 else tf.reshape(a, [1] + a_shape)
    b = b if len(b_shape) > 1 else tf.reshape(b, [1] + b_shape)

    res.base_object = tf.matmul(a, b, transpose_a, transpose_b, adjoint_a, adjoint_b, a_is_sparse, b_is_sparse, name)

    return res


def dot(x,y):

    x_shape = shape_to_list(x)
    y_shape = shape_to_list(y)

    if len(x_shape) == 1 and len(y_shape)==2:

        a = y
        b = x

    elif len(x_shape) == 2 and len(y_shape) == 1:
        a = x
        b = y


    else:
        raise ValueError("Wrong dimensions")


    return matmul(a, b, transpose_b=True)



def shape_to_list(a):

    if isinstance(a, inferpy.models.RandomVariable):
        a_shape = a.shape
    elif isinstance(a, np.ndarray):
        a_shape = list(a.shape)
    elif isinstance(a, list):
        a_shape = list(np.shape(a))
    elif isinstance(a, tf.Tensor):
        a_shape = a._shape_as_list()
    else:
        raise ValueError("Wrong input type "+a)

    return a_shape


def fix_shape(s):

    ret = []

    for i in range(0,len(s)):
        if i in [0, len(s)-1] or s[i] != 1:
            ret.append(s[i])

    if len(ret) == 0:
        return [1]

    return ret






