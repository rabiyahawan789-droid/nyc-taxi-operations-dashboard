# NYC Taxi Operations & Revenue Dashboard

An end-to-end data analytics project analyzing NYC taxi trip operations, demand patterns, revenue performance, payment behavior, and trip efficiency using Python and Tableau.

## Project Overview

This project transforms raw NYC taxi trip data into a structured analytical dataset and an interactive Tableau dashboard designed to answer key operational and business questions.

The analysis focuses on:

- Trip volume and demand patterns
- Pickup-zone performance
- Hourly trip demand
- Revenue trends
- Payment method distribution
- Trip efficiency by hour
- Revenue performance across pickup zones

## Business Questions

The project investigates:

1. Which pickup zones generate the highest trip volumes?
2. When is taxi demand highest throughout the day?
3. How does revenue vary by pickup hour?
4. Which payment methods dominate taxi transactions?
5. At which hours is trip efficiency highest?
6. Which pickup zones generate the highest average revenue?
7. What operational patterns can help improve taxi fleet planning?

   ## Key Insights

### Demand & Revenue

- The dataset contains **3.23 million cleaned taxi trips** from January 2025.
- Demand varies substantially by hour, with trip volume reaching **135,882 trips at 09:00** among the hourly results.
- Average revenue per trip varies considerably throughout the day. It reaches approximately **$34.73 at 05:00**, compared with approximately **$24.07 at 02:00**.
- Pickup-zone performance differs significantly: high-volume Manhattan zones generate large trip volumes, while airport zones generate substantially higher revenue per trip.

### Payment Behavior

- **Credit card** payments account for approximately **2.40 million trips**, making them the dominant payment method in the cleaned dataset.
- Credit-card trips generate approximately **$67.2 million in revenue** and have an average revenue of approximately **$27.95 per trip**.
- Credit-card trips also show a substantially higher average tip rate than cash and other payment categories.

### Rate-Type Performance

- **Standard-rate trips** dominate the dataset with approximately **2.66 million trips**.
- JFK trips have an average revenue of approximately **$93.98 per trip**, substantially above the standard-rate average of approximately **$24.51**.
- Negotiated-fare trips show unusually high fare-per-mile values; because their volume is relatively small, these results should be interpreted cautiously rather than generalized across the taxi fleet.

### Operational Efficiency

- Trip duration per mile varies considerably by pickup hour.
- The hourly analysis indicates that slower travel conditions occur during specific high-traffic periods, making **duration per mile** a useful operational-efficiency indicator.
- Efficiency metrics should be interpreted alongside trip volume and distance because very short trips can produce unusually high fare-per-mile or duration-per-mile values.

### Business Implications

- Driver capacity should be concentrated around high-demand time periods and high-volume pickup zones.
- Airport trips represent an important high-value segment and can be considered separately from standard Manhattan demand.
- Payment and rate-type differences suggest that revenue optimization should consider **trip type and customer/payment behavior**, rather than relying on trip volume alone.

## Tech Stack

- **Python** — Data cleaning, transformation, and analysis
- **Pandas** — Data manipulation and aggregation
- **Jupyter Notebook** — Exploratory Data Analysis
- **Tableau** — Interactive visualization and dashboard development
- **Git & GitHub** — Version control and project management
## Project Workflow

Raw NYC Taxi Data
↓
Data Cleaning & Transformation
↓
Feature Engineering & Aggregation
↓
Processed Analytical Datasets
↓
Tableau Visualization
↓
Interactive Operations & Revenue Dashboard

## Interactive Tableau Dashboard

View the full interactive dashboard on Tableau Public:

[Open NYC Taxi Operations & Revenue Dashboard](https://public.tableau.com/views/NYCTaxiOperationsRevenueDashboard/Dashboard1?:language=en-US)

## Dashboard Preview

![NYC Taxi Operations & Revenue Dashboard](dashboard-preview.png)

