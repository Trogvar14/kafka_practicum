# /opt/app/sitecustomize.py
# Шимы совместимости для faust-streaming ↔ mode
import sys

# 1) В старом mode нет compat.OrderedDict
try:
    import mode.utils.compat as compat
    from collections import OrderedDict as _OrderedDict
    if not hasattr(compat, "OrderedDict"):
        compat.OrderedDict = _OrderedDict
except Exception as e:
    print(f"[sitecustomize] compat patch skipped: {e}", file=sys.stderr)

# 2) В старом mode нет contexts.nullcontext
try:
    import mode.utils.contexts as contexts
    from contextlib import nullcontext as _nullcontext
    if not hasattr(contexts, "nullcontext"):
        contexts.nullcontext = _nullcontext
except Exception as e:
    print(f"[sitecustomize] contexts patch skipped: {e}", file=sys.stderr)
