# Statistical Inference on Tech Salaries and Layoffs

**Course project — Statistical Inference, Semester 5**
Moksh Barapatre · Section B3 · Roll no. 49

This project applies descriptive statistics and classical inferential methods to two datasets: a sample of **12,958 Indian salary postings** and **557 reported layoff events** from a 2026 snapshot. The complete analysis lives in a single executed Jupyter notebook, from exploratory data analysis through sampling, the Central Limit Theorem, hypothesis tests, ANOVA, and linear regression, and ends with an optional Gradio salary predictor.

## Repository contents

| File | Description |
| --- | --- |
| [`B3_B3_49_Moksh.ipynb`](B3_B3_49_Moksh.ipynb) | Main notebook with code, plots, printed results, and interpretation |
| [`india_salary_benchmarks_2026_sample.csv`](india_salary_benchmarks_2026_sample.csv) | Salary posting sample (12,958 rows × 14 columns) |
| [`layoffs-2026.csv`](layoffs-2026.csv) | Layoff event snapshot (557 rows × 8 columns) |
| [`requirements.txt`](requirements.txt) | Python dependencies |
| [`README.md`](README.md) | Project overview and run instructions |

## Datasets

### India salary benchmarks 2026 (sample)

- **Source:** [Fliar BI — India Salary Data 2026](https://fliarbi.com/datasets/india-salary-benchmarks-2026/)
- **Coverage:** postings from **January 2024 to June 2026** (30 distinct months)
- **Sample size:** 12,958 postings from 2,614 employers across 387 cities
- **Target variable:** `salary_mid_inr`, the midpoint of the advertised annual salary range in INR

| Column | Description |
| --- | --- |
| `posting_id` | Unique posting identifier |
| `posted_month` | Posting month (`YYYY-MM`) |
| `company`, `company_domain` | Employer name and domain |
| `job_title` | Advertised job title |
| `role_family` | Normalized role group (e.g. `software-eng`, `data`, `sales`) |
| `seniority` | Entry, mid, senior, lead, manager, intern |
| `experience_band` | Requested experience band |
| `city` | Posting city |
| `industry_category` | Industry label |
| `salary_min_inr`, `salary_max_inr`, `salary_mid_inr` | Annual salary range and its midpoint (INR) |
| `fliar_profile_url` | Link to the source posting, when available |

The supplied file is a **sample** of the 49,355 postings listed on the source page. Missing values are retained and handled explicitly: `industry_category` is missing in 6,380 rows, `company_domain`/`fliar_profile_url` in 11,519, `experience_band` in 1,093, `seniority` in 955, `city` in 341, and `salary_min_inr` in 245. `salary_mid_inr` is complete and positive for every row.

### Layoffs 2026

- **Source:** [LayoffHedge](https://layoffhedge.com/data/layoffs-2026.csv) (snapshot generated 2026-10-26)
- **Size:** 557 events, **710,521 reported people cut**
- **Categories:** `RESTRUCTURE` (311), `AI-DRIVEN` (92), `COST CUT` (77), `WEAK DEMAND` (47), `MERGER` (30)
- **Tech share:** 124 events, the largest industry group in the file

| Column | Description |
| --- | --- |
| `Company` | Employer named in the report |
| `Industry` | Industry group |
| `People Cut` | Reported number of affected employees |
| `Workforce %` | Share of the employer's workforce affected |
| `Total Workforce` | Employer workforce size |
| `Date` | Report date as month and day (e.g. `Oct 23`) |
| `Category` | Reason category |
| `Source URL` | Original news or filing link |

The file is a **reported-event snapshot, not a complete time series**. Dates have no year column, so the notebook parses them as **2026**; 30 rows use non-standard values such as `2025-26`, `Feb 2026`, or `2026` and become missing dates rather than being forced into a date.

## What the notebook covers

1. **Environment and data loading** — library versions, local CSV loading, schema inspection.
2. **Source validation** — live HTTP checks of the salary page and layoffs CSV, HTML parsing with BeautifulSoup, and table extraction.
3. **Exploratory data analysis and cleaning** — missing-value audit, duplicate checks, numeric conversion, `month_index` feature creation, histograms and boxplots, IQR outlier flagging (1,226 flagged, not removed), salary by role, layoffs by month and industry.
4. **Sampling and distributions** — reproducible random sample of 300 postings compared with the full sample; observed salary density against a reference normal curve.
5. **Central Limit Theorem** — 1,000 resamples each at *n* = 5, 20, and 50, comparing the simulated standard error with the theoretical value.
6. **Hypothesis testing** — independent two-sample t-test for the two largest role groups, plus a large-sample z-test approximation.
7. **One-way ANOVA** — salary comparison across the five largest role groups, with a boxplot and group summary.
8. **Simple linear regression** — salary as a function of posting-month index, with MAE, MSE, RMSE, R², and residual diagnostics.
9. **Multiple linear regression** — adds role family, seniority, city, and industry through an imputation + one-hot encoding pipeline; the two models are compared on a held-out test set.
10. **Gradio demo** — an interactive salary estimate by posting month, disabled by default for clean notebook runs.

## Key results

Results from the committed notebook run:

| Analysis | Result | Interpretation |
| --- | --- | --- |
| Salary descriptives | Mean **₹10,16,847**, median **₹6,00,000**, *n* = 12,958 | The distribution is strongly right-skewed, so the median is the more representative center. |
| t-test: `software-eng` vs `sales` | *t* = **13.38**, *p* ≈ **3.49 × 10⁻⁴⁰** | Reject *H₀*: the two role groups have different mean salary midpoints. |
| z-test approximation | *z* = **15.16**, *p* ≈ **6.26 × 10⁻⁵²** | Same conclusion at large-sample scale. |
| One-way ANOVA (5 roles) | *F* = **82.80**, *p* ≈ **4.94 × 10⁻⁶⁹** | Reject *H₀*: at least one role-family mean differs. |
| Simple regression (month only) | R² = **0.017**, MAE = **₹7,65,155**, RMSE = **₹12,53,514** | Posting month alone explains almost none of the salary variation. |
| Multiple regression | R² = **0.294**, MAE = **₹5,86,312**, RMSE = **₹10,62,540** | Role, seniority, city, and industry add substantial explanatory power, but the fit is still modest. |

The t-test and ANOVA establish that the groups differ; they do **not** establish that role family causes the difference. Seniority, location, industry, and employer mix are plausible confounders.

## How to run

### Local Jupyter

```bash
git clone https://github.com/Arsen1c-18/SI-Project-Tech-Layoffs-and-Salaries.git
cd SI-Project-Tech-Layoffs-and-Salaries

python3.13 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

jupyter lab
```

Open `B3_B3_49_Moksh.ipynb` and run all cells from top to bottom. Keep both CSV files in the same directory as the notebook.

### Google Colab

Upload the notebook and both CSV files to the same Colab session, then choose **Runtime → Run all**.

### Notes on execution

- **Python 3.13** is recommended; the committed outputs were produced with Python 3.13.
- The notebook uses `SEED = 42` for reproducible sampling and train/test splits.
- The live source-validation cells require an internet connection. The core analysis itself only needs the two local CSV files.
- **Gradio is disabled by default.** In the setup cell, set `RUN_GRADIO_DEMO = True` and run the demo cell to launch the interface. The notebook will then print a local or temporary share URL. The app is a simple month-based estimate, not a production salary calculator.
- Live URLs and share links are temporary. The checked URLs returned HTTP 200 when the notebook was last executed.

## Reproducibility

- Random seed: `SEED = 42`
- Notebook outputs are committed, so plots and metrics can be reviewed without running anything.
- Core package versions used for the committed run are pinned in [`requirements.txt`](requirements.txt); notebook and runtime tooling use minimum versions. The first cell prints the installed versions.
- Re-running the notebook refreshes split-dependent metrics slightly if library versions or data change.

## Limitations

- This is an **observational analysis**. Significant tests describe differences in the supplied data; they do not identify causal effects.
- The salary file is a **sample**, not the full 49,355-posting population, and it covers postings with stated salaries only. Selection and reporting bias are likely.
- Salary outliers are flagged but retained, because high advertised salaries can be genuine. Winsorizing or robust models would be a reasonable extension.
- The layoffs file is a snapshot of reported events with no year field and 30 non-standard dates. Monthly layoff totals are therefore descriptive and incomplete.
- The simple regression uses posting month as a linear time proxy. Its very low R² means it should not be used for real salary forecasts.
- The multiple regression captures only the available categorical fields and uses linear regression on a skewed target; a log-transformed target or regularized model may perform better.
- The Gradio interface demonstrates deployment, not predictive validity.

## Data sources and attribution

- **Salary data:** Fliar BI, *India Salary Data 2026: 49k Job Postings* — <https://fliarbi.com/datasets/india-salary-benchmarks-2026/>. Licensed under **CC BY-NC 4.0**; the sample is redistributed here for non-commercial coursework with attribution.
- **Layoffs data:** LayoffHedge — <https://layoffhedge.com/data/layoffs-2026.csv>. The file header states *“Free to use with attribution”*; attribution is provided here.

## License

The analysis code and notebook are shared for educational and portfolio purposes. The datasets remain under the terms set by their original publishers, including the **CC BY-NC 4.0** license for the salary sample. Do not redistribute the data commercially. Contact the author for reuse beyond these terms.

## Author

**Moksh Barapatre**
Section B3 · Roll no. 49
GitHub: [@Arsen1c-18](https://github.com/Arsen1c-18)
