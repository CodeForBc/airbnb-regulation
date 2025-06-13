#!/bin/bash

CRON_JOB="0 0 * * * curl -s http://localhost:8001/listings/harvest-listings/ > /dev/null 2>&1"

# Check if the cron job already exists
crontab -l 2>/dev/null | grep -F "$CRON_JOB" >/dev/null

if [ $? -eq 0 ]; then
  echo "Cron job already exists."
else
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo "Cron job added successfully."
fi
