---
name: parse-aqi
description: Use this skill whenever we need to parse responses from aqi.in portal for AQI data
---

# Parse AQI

## Instructions
- Iterate over the list of cities provided in cities.md file and construct the URL `https://apiserver.aqi.in/aqi/v2/getAqiCalender?slug={{cityName}}&slugType=cityId&sensorname=aqi&year=2026&source=web`  
- Do a http get on this URL and receive a JSON response
- If getting authentication error add the request header `Authorization` with value `bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySUQiOjEsImlhdCI6MTc4MTUwNzAwMCwiZXhwIjoxNzgyMTExODAwfQ.4isyIsNnq3OKtwm1PC13MP-xegvO8tedlG5MIkL7KVw`

## Examples
- Parsing of aqi.in responses for cities
