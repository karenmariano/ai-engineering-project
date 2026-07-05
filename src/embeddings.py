"""Small deterministic embedding function for Chroma.

This avoids downloading a large model during Render builds while keeping the
project fully reproducible. It works well for the synthetic policy corpus
because section text and user questions share policy vocabulary and numbers.
"""

from __future__ import annotations

import hashlib
import math
import re

import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from chromadb.utils import embedding_functions


TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")


class HashingEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, dimensions: int = 768) -> None:
        self.dimensions = dimensions

    def __call__(self, input: Documents) -> Embeddings:
        return [self._embed(text) for text in input]

    def _embed(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimensions, dtype=np.float32)
        tokens = TOKEN_RE.findall((text or "").lower())
        if not tokens:
            return vec

        terms = list(tokens)
        terms.extend(f"{a}_{b}" for a, b in zip(tokens, tokens[1:]))
        for term in terms:
            digest = hashlib.blake2b(term.encode("utf-8"), digest_size=8).digest()
            n = int.from_bytes(digest, "big")
            idx = n % self.dimensions
            sign = 1.0 if (n >> 63) == 0 else -1.0
            vec[idx] += sign

        norm = math.sqrt(float(np.dot(vec, vec)))
        if norm:
            vec /= norm
        return vec


def embedding_function(model_name: str) -> EmbeddingFunction[Documents]:
    if model_name in ("default", "onnx-minilm"):
        return embedding_functions.DefaultEmbeddingFunction()
    if model_name.startswith("hashing"):
        parts = model_name.split("-", 1)
        dims = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 768
        return HashingEmbeddingFunction(dimensions=dims)
    raise ValueError(
        f"Unsupported EMBEDDING_MODEL={model_name!r}. Use 'default', 'onnx-minilm', "
        "'hashing', or 'hashing-<dimensions>'."
    )
