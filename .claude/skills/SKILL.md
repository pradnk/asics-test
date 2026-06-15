---
name: parse-aqi
description: Use this skill whenever we need to parse responses from aqi.in portal for AQI data
---

# Parse AQI

## Instructions
- Iterate over the list of cities provided in cities.md file and construct the URL `https://apiserver.aqi.in/aqi/v2/getAqiCalender?slug={{cityName}}&slugType=cityId&sensorname=aqi&year=2026&source=web`  
- Do a http get on this URL and receive a JSON response
- If getting authentication error add the necessary cookies to work

## Examples
- Parsing of aqi.in responses for cities
