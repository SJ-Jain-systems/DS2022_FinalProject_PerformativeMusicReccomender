# Mini Music Recommender API (Content-Based)

## 1) Executive Summary
**Problem.** People want fast music recommendations without relying on external APIs or heavy ML systems.  
**Solution.** This project is a lightweight microservice that ingests a curated music dataset, builds TF-IDF embeddings, stores results in SQLite, and serves similarity-based recommendations through a Flask REST API.

## 2) System Overview
**Course Concepts Used.**
- Data Pipeline / ETL: CSV → clean → build text blob → TF-IDF → persist  
- Flask REST API service  
- Logging + config via environment variables  
- SQLite schema for persistence  
- Validation tests

**Architecture.**
`music.csv → pipeline.py → TF-IDF vectors → SQLite recs.db → Flask API`

## 3) How to Run

### Docker (one command)
1. Copy env:
```bash
cp .env.example .env
