# Dataset

`eia_net_generation_2020_2024.csv` is a subset of a public U.S. government table.

- Publisher: U.S. Energy Information Administration
- Table: State Historical Tables, net generation by state, type of producer, and energy source
- File: `annual_generation_state.xls`
- Source page: https://www.eia.gov/electricity/data/state/
- Workbook note: "State Historical Tables for 2024. Released: September 2025. Next Update: October 2026."
- Retrieved: 13 October 2026

Rows kept:

- Years 2020 through 2024
- Producer type "Total Electric Power Industry"
- Every energy source except the "Total" row, so a sum is not counted twice
- `US-TOTAL` and `US-Total` stored as `US`

Values are net generation in megawatthours, as published. This repository does not include the original workbook. `scripts/build_csv.py` can rebuild the CSV from that workbook.
