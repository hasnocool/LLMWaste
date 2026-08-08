# tests/test_models.py
import pytest

from llmwaste.models import MODEL_CATALOG, get_model


def test_catalog_keys_are_unique() -> None:
    keys = [model.key for model in MODEL_CATALOG]
    assert len(keys) == len(set(keys))


def test_sparse_targets_have_small_active_fraction() -> None:
    model = get_model("kimi-linear-48b-a3b-instruct")
    assert model.active_fraction < 0.10


def test_unknown_model_raises() -> None:
    with pytest.raises(KeyError):
        get_model("missing")
