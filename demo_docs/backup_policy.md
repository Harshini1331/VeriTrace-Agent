# SOP-IT-05: Data Backup and Recovery Procedures

## 1. Overview
This document outlines the procedures for backing up critical business data to ensure recoverability in the event of system failure, data corruption, or disaster.

## 2. Backup Schedule
- **Full Backups:** Performed weekly on Sundays at 02:00 UTC.
- **Incremental Backups:** Performed daily at 03:00 UTC.
- **Transaction Logs:** Backed up every 15 minutes for point-in-time recovery.

## 3. Retention Policy
As per GISP Rule 2.1, all backup sets are retained according to the following schedule:
- **Daily Backups:** Retained for 14 days.
- **Weekly Backups:** Retained for 90 days.
- **Monthly Backups:** Retained for 1 year (archived to cold storage).

## 4. Testing & Verification
- Automated integrity checks are run on every backup job.
- A full restoration test is conducted quarterly to verify RTO/RPO targets.
