# EcoFit API Guide (A1 Level)

## 1. Introduction
EcoFit connects to external web services (APIs) to get weather data, news, and business charts.

---

## 2. Open-Meteo API (Weather)
* **What it does:** Gets the current outdoor temperature when a user saves a workout.
* **Type:** Free REST API.
* **How it works:** 
  1. EcoFit sends latitude and longitude coordinates.
  2. Open-Meteo sends back the current temperature.
  3. EcoFit saves the temperature in `bd_atividades`.

---

## 3. Google News API (Sports News)
* **What it does:** Displays current sports news and athletic events on the main page.
* **How it works:** 
  1. The app searches for fitness and sports news.
  2. It shows titles and links at the bottom of the dashboard.

---

## 4. Power BI Pipeline (Data Reports)
* **What it does:** Creates advanced business dashboards and charts.
* **How it works:**
  1. EcoFit exports database records into a standard `.csv` file.
  2. The file is uploaded automatically to a public **Supabase Storage** bucket (`export-powerbi`).
  3. Power BI reads the file from the web link and updates all reports.