# translator.py
# Translation examples and API mapping for PyTorch -> JAX
# In the real system this would wrap an LLM, but for now it's just
# example pairs and the mapping table

TRANSLATION_EXAMPLES = {
    "matrix_ops": {
        "pytorch": """
import torch

def matmul_kernel(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    return torch.matmul(A, B)
""",
        "jax": """
import jax.numpy as jnp

def matmul_kernel(A: jnp.ndarray, B: jnp.ndarray) -> jnp.ndarray:
    return jnp.matmul(A, B)
"""
    },
    "normalization": {
        "pytorch": """
import torch
import torch.nn.functional as F

def layer_norm(x: torch.Tensor, weight: torch.Tensor, bias: torch.Tensor, eps: float = 1e-5):
    mean = x.mean(dim=-1, keepdim=True)
    var = x.var(dim=-1, keepdim=True, unbiased=False)
    return weight * (x - mean) / torch.sqrt(var + eps) + bias
""",
        "jax": """
import jax.numpy as jnp

def layer_norm(x: jnp.ndarray, weight: jnp.ndarray, bias: jnp.ndarray, eps: float = 1e-5):
    mean = jnp.mean(x, axis=-1, keepdims=True)
    var = jnp.var(x, axis=-1, keepdims=True)
    return weight * (x - mean) / jnp.sqrt(var + eps) + bias
"""
    },
    "activation": {
        "pytorch": """
import torch

def gelu(x: torch.Tensor) -> torch.Tensor:
    return 0.5 * x * (1.0 + torch.erf(x / 1.4142135623730951))
""",
        "jax": """
import jax.numpy as jnp
from jax.scipy.special import erf

def gelu(x: jnp.ndarray) -> jnp.ndarray:
    return 0.5 * x * (1.0 + erf(x / 1.4142135623730951))
"""
    },
    "attention": {
        "pytorch": """
import torch
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    attn = F.softmax(scores, dim=-1)
    return torch.matmul(attn, V)
""",
        "jax": """
import jax.numpy as jnp
from jax.nn import softmax
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    d_k = Q.shape[-1]
    scores = jnp.matmul(Q, jnp.swapaxes(K, -2, -1)) / math.sqrt(d_k)
    if mask is not None:
        scores = jnp.where(mask == 0, float('-inf'), scores)
    attn = softmax(scores, axis=-1)
    return jnp.matmul(attn, V)
"""
    },
    "reduction": {
        "pytorch": """
import torch

def global_avg_pool(x: torch.Tensor) -> torch.Tensor:
    return x.mean(dim=[2, 3])
""",
        "jax": """
import jax.numpy as jnp

def global_avg_pool(x: jnp.ndarray) -> jnp.ndarray:
    return jnp.mean(x, axis=(2, 3))
"""
    }
}

# pytorch -> jax API mapping
# might not be 100% complete but covers the common stuff
API_MAPPING = {
    "torch.matmul": "jnp.matmul",
    "torch.sum": "jnp.sum",
    "torch.mean": "jnp.mean",
    "torch.sqrt": "jnp.sqrt",
    "torch.exp": "jnp.exp",
    "torch.log": "jnp.log",
    "torch.relu": "jax.nn.relu",
    "torch.sigmoid": "jax.nn.sigmoid",
    "torch.tanh": "jnp.tanh",
    "torch.softmax": "jax.nn.softmax",
    "torch.cat": "jnp.concatenate",
    "torch.stack": "jnp.stack",
    "torch.reshape": "jnp.reshape",
    "torch.transpose": "jnp.transpose",
    "torch.unsqueeze": "jnp.expand_dims",
    "torch.squeeze": "jnp.squeeze",
    "torch.zeros": "jnp.zeros",
    "torch.ones": "jnp.ones",
    "torch.randn": "jax.random.normal",
    "torch.arange": "jnp.arange",
    "F.softmax": "jax.nn.softmax",
    "F.relu": "jax.nn.relu",
    "F.gelu": "jax.nn.gelu",
    "F.dropout": "# JAX dropout requires PRNGKey",
    ".size()": ".shape",
    ".dim()": ".ndim",
    ".view(": ".reshape(",
    ".permute(": ".transpose(",
    ".contiguous()": "# not needed in JAX",
    ".cuda()": "# JAX handles device placement",
    ".to(device)": "# JAX handles device placement",
}


def get_translation_example(category):
    """Look up a translation example by kernel category."""
    return TRANSLATION_EXAMPLES.get(category, None)


def get_api_mapping():
    return API_MAPPING
