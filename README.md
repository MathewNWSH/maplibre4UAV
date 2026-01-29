# maplibre4UAV

Dynamic tile server for UAV/drone imagery using VRT files with MapLibre visualization.

## Features

- **rio-tiler + FastAPI** backend for dynamic VRT tile serving
- **MapLibre GL JS** frontend for interactive map visualization
- **GDAL optimized** Docker setup for high performance
- **No format conversion** - serves VRT files directly
- **S3 ready** - placeholders for cloud storage credentials

## Quick Start

```bash
# Clone and configure
cp .env.example .env
# Edit .env with your data paths

# Start services
docker compose up -d

# Open browser
# Frontend: http://localhost:8080
# API docs: http://localhost:8000/docs
```

## Configuration

Edit `.env` file:

```bash
# Path to VRT files
DATA_DIR=/path/to/your/vrts

# Path to source images (JPG/TIFF) referenced by VRTs
SOURCE_DIR=/path/to/source/images
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /datasets` | List available VRT datasets |
| `GET /datasets/{name}/info` | Dataset metadata |
| `GET /datasets/{name}/bounds` | Geographic bounds |
| `GET /datasets/{name}/tilejson.json` | TileJSON for MapLibre |
| `GET /datasets/{name}/tiles/{z}/{x}/{y}.{format}` | Tile rendering (png/jpg/webp) |

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   MapLibre GL   │────▶│  FastAPI + rio  │
│   (frontend)    │     │    -tiler       │
│   :8080         │     │   :8000         │
└─────────────────┘     └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │   VRT + GDAL    │
                        │   (optimized)   │
                        └────────┬────────┘
                                 │
                        ┌────────▼────────┐
                        │  Source Images  │
                        │  (JPG/TIFF)     │
                        └─────────────────┘
```

## GDAL Performance Tuning

The Docker image includes optimized GDAL settings:

| Variable | Value | Purpose |
|----------|-------|---------|
| `GDAL_CACHEMAX` | 200 | Block cache 200MB |
| `GDAL_MAX_DATASET_POOL_SIZE` | 200 | Dataset pool size |
| `GDAL_NUM_THREADS` | ALL_CPUS | Multi-threading |
| `VSI_CACHE` | TRUE | File caching |
| `GDAL_DISABLE_READDIR_ON_OPEN` | EMPTY_DIR | Skip dir scanning |

## S3 Support (Future)

Uncomment S3 variables in `docker-compose.yml`:

```yaml
AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
AWS_DEFAULT_REGION: "${AWS_DEFAULT_REGION}"
```

## License

MIT
