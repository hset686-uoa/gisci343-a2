# Auckland Public Transport Patronage Dashboard

Interactive dashboard exploring Auckland public transport usage patterns between 2023 and 2026.

## Features
- Top routes by passenger numbers
- Monthly patronage trends
- Interactive filters
- Spatial bus stop map

## Technologies
- Python
- Shiny for Python
- Pandas
- Matplotlib
- ipyleaflet
- Shinylive

## Setup

Install dependencies:

```bash
uv sync
```

Run locally:

```bash
shiny run --reload app.py
```

## Deployment

Export Shinylive site:

```bash
uv run shinylive export . docs
```

Hosted using GitHub Pages.

## Live App
[Dashboard Link](https://hset686-uoa.github.io/gisci343-a2/)
