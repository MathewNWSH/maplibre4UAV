"""Dynamic tile server for VRT files using rio-tiler + FastAPI."""

import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from rio_tiler.io import Reader
from rio_tiler.errors import TileOutsideBounds

app = FastAPI(
    title="maplibre4UAV Tile Server",
    description="Dynamic tile server for UAV/drone VRT imagery",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/datasets")
def list_datasets():
    """List available VRT datasets."""
    vrts = list(DATA_DIR.glob("**/*.vrt"))
    return {
        "datasets": [
            {"name": vrt.stem, "path": str(vrt.relative_to(DATA_DIR))}
            for vrt in sorted(vrts, key=lambda x: x.stem)
        ]
    }


@app.get("/datasets/{dataset}/info")
def dataset_info(dataset: str):
    """Get dataset metadata."""
    vrt_path = DATA_DIR / f"{dataset}.vrt"
    if not vrt_path.exists():
        vrt_path = next(DATA_DIR.glob(f"**/{dataset}.vrt"), None)

    if not vrt_path or not vrt_path.exists():
        return Response(status_code=404, content=f"Dataset {dataset} not found")

    with Reader(str(vrt_path)) as src:
        info = src.info()
        return {
            "name": dataset,
            "bounds": info.bounds,
            "crs": str(info.crs),
            "width": info.width,
            "height": info.height,
            "band_metadata": info.band_metadata,
            "band_descriptions": info.band_descriptions,
            "dtype": info.dtype,
            "minzoom": getattr(info, "minzoom", 0),
            "maxzoom": getattr(info, "maxzoom", 22),
        }


@app.get("/datasets/{dataset}/bounds")
def dataset_bounds(dataset: str):
    """Get dataset bounds for MapLibre."""
    vrt_path = DATA_DIR / f"{dataset}.vrt"
    if not vrt_path.exists():
        vrt_path = next(DATA_DIR.glob(f"**/{dataset}.vrt"), None)

    if not vrt_path or not vrt_path.exists():
        return Response(status_code=404, content=f"Dataset {dataset} not found")

    with Reader(str(vrt_path)) as src:
        info = src.info()
        bounds = info.bounds
        return {
            "bounds": [bounds[0], bounds[1], bounds[2], bounds[3]],
            "center": [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2],
            "minzoom": getattr(info, "minzoom", 0),
            "maxzoom": getattr(info, "maxzoom", 22),
        }


@app.get("/datasets/{dataset}/tilejson.json")
def tilejson(
    dataset: str,
    tile_format: Annotated[str, Query()] = "png",
):
    """TileJSON endpoint for MapLibre."""
    vrt_path = DATA_DIR / f"{dataset}.vrt"
    if not vrt_path.exists():
        vrt_path = next(DATA_DIR.glob(f"**/{dataset}.vrt"), None)

    if not vrt_path or not vrt_path.exists():
        return Response(status_code=404, content=f"Dataset {dataset} not found")

    with Reader(str(vrt_path)) as src:
        info = src.info()
        bounds = info.bounds

        return {
            "tilejson": "3.0.0",
            "name": dataset,
            "tiles": [f"/datasets/{dataset}/tiles/{{z}}/{{x}}/{{y}}.{tile_format}"],
            "bounds": [bounds[0], bounds[1], bounds[2], bounds[3]],
            "center": [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2, 15],
            "minzoom": getattr(info, "minzoom", 0),
            "maxzoom": getattr(info, "maxzoom", 22),
        }


@app.get("/datasets/{dataset}/tiles/{z}/{x}/{y}.{format}")
def get_tile(
    dataset: str,
    z: int,
    x: int,
    y: int,
    format: str = "png",
):
    """Get a single tile."""
    vrt_path = DATA_DIR / f"{dataset}.vrt"
    if not vrt_path.exists():
        vrt_path = next(DATA_DIR.glob(f"**/{dataset}.vrt"), None)

    if not vrt_path or not vrt_path.exists():
        return Response(status_code=404, content=f"Dataset {dataset} not found")

    try:
        with Reader(str(vrt_path)) as src:
            img = src.tile(x, y, z, tilesize=256)

            if format == "png":
                content = img.render(img_format="PNG")
                media_type = "image/png"
            elif format in ("jpg", "jpeg"):
                content = img.render(img_format="JPEG", quality=85)
                media_type = "image/jpeg"
            elif format == "webp":
                content = img.render(img_format="WEBP", quality=85)
                media_type = "image/webp"
            else:
                content = img.render(img_format="PNG")
                media_type = "image/png"

            return Response(
                content=content,
                media_type=media_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                },
            )
    except TileOutsideBounds:
        return Response(status_code=204)
    except Exception as e:
        return Response(status_code=500, content=str(e))


@app.get("/tiles/{z}/{x}/{y}.{format}")
def get_tile_by_url(
    z: int,
    x: int,
    y: int,
    format: str = "png",
    url: Annotated[str, Query(description="Path to VRT file")] = "",
):
    """Get tile by URL parameter (TiTiler-compatible endpoint)."""
    if not url:
        return Response(status_code=400, content="url parameter required")

    if url.startswith("/"):
        vrt_path = Path(url)
    else:
        vrt_path = DATA_DIR / url

    if not vrt_path.exists():
        return Response(status_code=404, content=f"File not found: {url}")

    try:
        with Reader(str(vrt_path)) as src:
            img = src.tile(x, y, z, tilesize=256)

            if format == "png":
                content = img.render(img_format="PNG")
                media_type = "image/png"
            elif format in ("jpg", "jpeg"):
                content = img.render(img_format="JPEG", quality=85)
                media_type = "image/jpeg"
            elif format == "webp":
                content = img.render(img_format="WEBP", quality=85)
                media_type = "image/webp"
            else:
                content = img.render(img_format="PNG")
                media_type = "image/png"

            return Response(
                content=content,
                media_type=media_type,
                headers={
                    "Cache-Control": "public, max-age=3600",
                },
            )
    except TileOutsideBounds:
        return Response(status_code=204)
    except Exception as e:
        return Response(status_code=500, content=str(e))
