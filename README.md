<div align="center">

# 🍾 Vendor Performance Analysis

### Turning raw purchase & sales data into vendor, pricing, and inventory decisions

[![Python](https://img.shields.io/badge/Python-pandas%20%7C%20seaborn%20%7C%20scipy-3776AB?logo=python&logoColor=white)](#tech-stack)
[![SQL](https://img.shields.io/badge/SQLite-Data%20Pipeline-07405e?logo=sqlite&logoColor=white)](#how-the-pipeline-works)
[![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-F2C811?logo=powerbi&logoColor=black)](powerbi/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Analysis%20Notebooks-F37626?logo=jupyter&logoColor=white)](notebooks/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](#)

*A vendor & inventory profitability analysis for a retail/wholesale distributor — from raw
purchase/sales data to a data pipeline, statistical analysis, a written report, and a Power BI
dashboard.*

</div>

<p align="center">
  <img src="images/04_top_vendors_bar.png" width="720" alt="Top 10 vendors by total sales">
</p>

---

## 📌 The Problem

A distributor wants to know: **which brands and vendors are actually driving profit**, where is
money getting stuck in unsold inventory, and where should pricing or vendor relationships
change? Specifically:

1. Which brands would benefit from a pricing or promotion push?
2. Which vendors contribute the most to sales and purchases?
3. Does buying in bulk actually lower unit cost?
4. Which vendors are sitting on slow-moving inventory?
5. Is the profitability gap between high- and low-volume vendors real, or just noise?

---

## 🔑 Key Findings

| Question | Finding |
|---|---|
| 🎯 Promo candidates | **198 brands** have low sales but high profit margin — proven margin, needs volume |
| 🏭 Vendor concentration | Top **10 vendors = 65.7%** of all purchases — a real supply-chain risk |
| 📦 Bulk buying | Large orders cost **72% less per unit** than small orders ($10.78 vs $39.06) |
| 💸 Dead stock | **$2.71M** of capital is tied up in unsold inventory |
| 📊 Margin gap | Low-volume vendors run **~10 points higher margin** than top vendors (41.6% vs 31.2%), confirmed with a Welch's t-test (p < 0.001) |

📄 Full write-up with charts: **[`report/Vendor_Performance_Report.pdf`](report/Vendor_Performance_Report.pdf)**

---

## 📊 A Look at the Analysis

<table>
<tr>
<td width="50%">

**Promotion candidates — proven margin, low volume**

<img src="images/02_brands_low_sales_high_margin.png" width="100%" alt="Brands with low sales but high profit margin">

</td>
<td width="50%">

**Vendor concentration — top 10 = 65.7% of purchases**

<img src="images/03_top_vendors_donut.png" width="100%" alt="Top 10 vendors purchase contribution donut chart">

</td>
</tr>
<tr>
<td width="50%">

**Bulk orders cost 72% less per unit**

<img src="images/05_bulk_purchasing_boxplot.png" width="100%" alt="Unit purchase price by order size boxplot">

</td>
<td width="50%">

**Margin gap: top vs. low-volume vendors (p < 0.001)**

<img src="images/06_profit_margin_histogram.png" width="100%" alt="Profit margin distribution top vs low vendors">

</td>
</tr>
</table>

<p align="center">
  <img src="images/01_correlation_heatmap.png" width="620" alt="Correlation heatmap across all numeric fields">
  <br>
  <sub>Correlation heatmap across all numeric fields, post-filtering</sub>
</p>

---

## ⚙️ How the Pipeline Works

```
raw CSVs (purchases, sales, purchase_prices, vendor_invoice)
        │
        ▼   scripts/ingestion_db.py
   inventory.db  (each CSV → its own SQL table)
        │
        ▼   scripts/get_vendor_summary.py  /  notebooks/01_data_pipeline.ipynb
   vendor_sales_summary  (one joined, cleaned table: 1 row per vendor + brand)
        │
        ├──▶ data/vendor_sales_summary.csv
        │        │
        │        ▼   notebooks/02_vendor_performance_analysis.ipynb
        │      EDA → filtering → 5 business questions → stats test → recommendations
        │
        └──▶ powerbi/vendor_performance.pbix  (interactive dashboard, same source CSV)
```

> **Why build a separate summary table instead of querying raw tables every time?**
> The raw tables are large, and every useful question needs data from more than one of them.
> Joining and aggregating once — down to ~10.7K rows — makes every downstream step (notebook
> or dashboard) fast and simple.

---

## 🗂️ Repo Structure

```
├── README.md                                   ← you are here
├── data/
│   └── vendor_sales_summary.csv                ← the analysis-ready table
├── scripts/
│   ├── ingestion_db.py                         ← raw CSVs → SQLite
│   └── get_vendor_summary.py                   ← joins + cleans → summary table
├── notebooks/
│   ├── 01_data_pipeline.ipynb                  ← documents the SQL/cleaning pipeline
│   └── 02_vendor_performance_analysis.ipynb    ← the actual analysis (runs standalone off the CSV)
├── report/
│   └── Vendor_Performance_Report.pdf           ← polished write-up with charts
├── powerbi/
│   ├── vendor_performance.pbix                 ← interactive dashboard
│   └── README.md                               ← how to rebuild/extend it
└── images/                                     ← charts used in the notebook & report
```

---

## ▶️ How to Run It

**Fastest path** — go straight to the analysis using the provided CSV:

```bash
pip install pandas numpy matplotlib seaborn scipy jupyter
jupyter notebook notebooks/02_vendor_performance_analysis.ipynb
```

**Full pipeline from raw data** (if you have the source CSVs):

```bash
pip install pandas sqlalchemy
python scripts/ingestion_db.py       # raw CSVs → inventory.db
python scripts/get_vendor_summary.py # build vendor_sales_summary → CSV + DB table
```

**Dashboard**: open `powerbi/vendor_performance.pbix` in Power BI Desktop, or see
[`powerbi/README.md`](powerbi/README.md) to rebuild it from the CSV.

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data pipeline | SQLite (joins/aggregation) |
| Analysis | Python — pandas, seaborn, matplotlib, scipy (hypothesis testing) |
| Dashboard | Power BI |
| Narrative | Jupyter |

---

## 🚀 What I'd Improve Next

- **Add a time dimension.** The current summary table is a single snapshot — no date field
  means no trend/seasonality analysis. That's the single highest-value addition.
- **Vendor segmentation model.** Cluster vendors by margin, volume, and turnover instead of
  eyeballing "top 10" — turns this from descriptive analysis into something predictive.
- **Delivery/lead-time data**, if available in the source system, would round out the
  vendor-risk story (right now it's purely a profitability view).
- **Sensitivity-test the thresholds** used for "low sales" / "high margin" (currently fixed
  percentiles) rather than treating them as given.
- The rows filtered out for the profitability analysis (losses, dead stock, zero-sale items)
  are a legitimate finding on their own and deserve a follow-up notebook rather than being
  discarded.

---

<div align="center">

📄 [Full Report (PDF)](report/Vendor_Performance_Report.pdf) · 📊 [Power BI Dashboard](powerbi/) · 📓 [Analysis Notebook](notebooks/02_vendor_performance_analysis.ipynb)

</div>
