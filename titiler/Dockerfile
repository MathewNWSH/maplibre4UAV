FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.4

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# GDAL Performance Tuning
ENV GDAL_CACHEMAX=200 \
    GDAL_MAX_DATASET_POOL_SIZE=200 \
    GDAL_NUM_THREADS=ALL_CPUS \
    GDAL_HTTP_MULTIPLEX=YES \
    GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES \
    GDAL_HTTP_VERSION=2 \
    GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR \
    GDAL_INGESTED_BYTES_AT_OPEN=32768 \
    VSI_CACHE=TRUE \
    VSI_CACHE_SIZE=5000000 \
    GDAL_BAND_BLOCK_CACHE=HASHSET \
    CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".vrt,.VRT,.jpg,.JPG,.jpeg,.JPEG,.tif,.TIF,.tiff,.TIFF"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV DATA_DIR=/data

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
