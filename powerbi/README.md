# Power BI Dashboard

## What changed

The original file had **one page with 12 visuals crammed together** (two bar charts
overlapping by ~50px, a funnel chart, and a scatter chart all fighting for space at the
bottom). It's been reorganized into **3 focused pages**, using the exact same data model
(no columns/measures were touched — this is a report-layer redesign, not a data change).

| Before | After |
|---|---|
| 1 page, 12 visuals | 3 pages, 12 visuals + a vendor slicer on 2 of them |
| Bar charts overlapping ~50px | Repositioned, no overlap |
| Funnel chart for ranking vendors by stock turnover | Bar chart (funnels imply a sequential drop-off; this is just a ranking) |
| Scatter chart titled "Low Performing Brands" | Retitled "Brands: Low Sales but High Margin — Promotion Candidates" (the original title was actively misleading — these are high-*margin* brands, not underperforming ones; the wrong label risks someone discontinuing a profitable line) |
| No detail table, no interactivity | Added a sortable vendor detail table (Overview) and a vendor slicer (Overview + Risk page) |

### Page 1 — Overview
KPI cards (Total Purchases, Total Sales, Gross Profit, Avg Profit Margin, Unsold Capital) +
vendor purchase-concentration donut + top vendors/brands by sales + a full vendor detail
table + a vendor slicer.

### Page 2 — Brand Opportunities
The relabeled scatter chart, full-size, next to a table listing just the 198 flagged
brands (low sales, high margin) — the promotion/pricing candidate list.

### Page 3 — Vendor & Inventory Risk
Unsold-inventory KPI, vendors ranked by stock turnover (now a bar chart), vendors ranked
by unsold inventory value, and a vendor slicer.

## A note on how this was built

This redesign was made by editing the report's layout file directly (outside Power BI
Desktop) and could not be tested against the real Power BI engine before delivery. The
data model itself was **not modified** — only the report/visuals layer — so the underlying
numbers are guaranteed correct. If Power BI Desktop shows a "couldn't load visual" warning
on any single visual after opening, right-click it → **Refresh visual** (or just resave the
file once) and it will rebuild its query cache. If a page looks off, the safe fallback is to
rebuild that one visual manually using the field list below.

## KPIs that were reviewed and kept as-is

- **Total Purchases / Total Sales / Gross Profit** — straightforward sums, no issues.
- **Avg Profit Margin %** — this is an *unweighted* average of `ProfitMargin` across every
  vendor-brand row, so a tiny $12 line item counts the same as a $500K one. That's a
  legitimate way to answer "what's typical," but for an executive KPI a **sales-weighted**
  margin (`Total Gross Profit / Total Sales`) tells a different, arguably more useful story.
  Worth adding as a second measure if you extend this:
  ```DAX
  Weighted Profit Margin % = DIVIDE(SUM(vendor_sales_summary[GrossProfit]), SUM(vendor_sales_summary[TotalSalesDollars])) * 100
  ```
- **Unsold Capital** — already a column in the model matching the notebook's
  `UnsoldInventoryValue` logic. Correct.

## Two findings that still aren't on the dashboard

The data model doesn't currently have the columns these need, and adding them requires
Power BI Desktop's engine (can't be done safely by hand-editing outside the app). Both are
quick to add:

**1. Bulk purchasing impact (72% unit-cost reduction) — needs 2 new columns:**
```DAX
UnitPurchasePrice = DIVIDE(vendor_sales_summary[TotalPurchaseDollars], vendor_sales_summary[TotalPurchaseQuantity])

OrderSize = SWITCH(
    TRUE(),
    vendor_sales_summary[TotalPurchaseQuantity] <= PERCENTILEX.INC(vendor_sales_summary, vendor_sales_summary[TotalPurchaseQuantity], 0.33), "Small",
    vendor_sales_summary[TotalPurchaseQuantity] <= PERCENTILEX.INC(vendor_sales_summary, vendor_sales_summary[TotalPurchaseQuantity], 0.66), "Medium",
    "Large"
)
```
Then add a **clustered column chart**: `OrderSize` on axis, `Average of UnitPurchasePrice` as value.

**2. Statistical margin comparison (top vs. low vendors, p < 0.001) — a dashboard card, not a chart:**
Since the t-test itself needs to run in Python/R (DAX doesn't have a t-test function),
the cleanest option is a **Python visual** pulling from `vendor_sales_summary`, pasting in
the `scipy.stats.ttest_ind` logic from `notebooks/02_vendor_performance_analysis.ipynb`
section 8. Simpler alternative: just add two card KPIs — "Top Vendor Avg Margin" and "Low
Vendor Avg Margin" — using measures with `CALCULATE` + `TOPN`/quartile filters, and note
the significance result in a text box.

## Rebuilding from scratch

If you'd rather start clean: `Get Data → Text/CSV → ../data/vendor_sales_summary.csv`,
set `VendorNumber`/`Brand` as whole numbers, `TotalSalesDollars` etc. as decimal, then
recreate the measures listed above. The three calculated tables already in the model
(`PurchaseContribution`, `LowTurnoverVendor`, `BrandPerformance`) mirror the notebook's
groupby logic in sections 5, 7, and 4 respectively — use those as your reference for the
DAX if you rebuild them.
