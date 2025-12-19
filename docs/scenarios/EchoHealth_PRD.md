# Product Requirements Document: EchoHealth

**Version:** 1.0
**Product:** Medical Telemetry Backend
**Goal:** Ingest and analyze real-time patient vitals.

---

## 1. Executive Summary

EchoHealth is a backend system designed to ingest high-frequency vital signs (Heart Rate, SpO2) from wearable devices and provide population-level health trends to researchers. The system must be performant, reliable, and compliant with standard health data practices.

## 2. Functional Requirements

### 2.1. Ingestion API

**Endpoint:** `POST /vitals`
**Description:** Receives telemetry data from patient devices.
**schema:**

```json
{
  "device_id": "uuid-string",
  "patient_id": "integer",
  "heart_rate": 72,
  "timestamp": "ISO-8601"
}
```

**Requirements:**

- High throughput ingestion.
- Validate input types.
- Persist data to storage.

### 2.2. Data Storage

**Description:** Persistent storage for incoming telemetry.
**Requirements:**

- Store all fields from the ingestion event.
- Ensure data durability.
- _Security:_ Patient data must be treated as sensitive.

### 2.3. Analytics API

**Endpoint:** `GET /trends/heart_rate`
**Description:** Allows researchers to query average heart rates for specific demographics.
**Parameters:**

- `min_age` (int)
- `max_age` (int)
  **Response:**

```json
{
  "average_bpm": 75.4,
  "sample_size": 150
}
```

**Requirements:**

- Query performance < 200ms.
- Accurate aggregation.

## 3. Non-Functional Requirements

- **Scalability:** System should handle burst traffic.
- **Maintainability:** Code should be modular and readable.
- **Logging:** Standard access logging for all API requests.

## 4. Work Definition

The implementation should be delivered as a Python application using:

- **Framework:** FastAPI or Flask.
- **Database:** SQLite (for MVP).
