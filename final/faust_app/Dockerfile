FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends openssl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
COPY requirements.txt ./

# ставим всё одной командой, выпиливаем старый robinhood-faust
RUN python -m pip install --upgrade pip \
 && python -m pip uninstall -y faust || true \
 && python -m pip install --no-cache-dir -r requirements.txt \
 && python - <<'PY'
import faust, mode, yarl
import mode.utils.compat as compat
print("faust:", getattr(faust, "__version__", "unknown"))
print("mode:", getattr(mode, "__version__", "unknown"))
print("yarl:", yarl.__version__)
print("compat has OrderedDict:", hasattr(compat, "OrderedDict"))
assert hasattr(compat,"OrderedDict"), "Wrong mode version — no OrderedDict in compat!"
PY

COPY app.py ./
CMD ["faust","-A","app","worker","-l","info"]