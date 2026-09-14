# Notebooks — Phase 1 lab

`01_forecast_api_colab.ipynb` is where you **practice** talking to the forecast API before you write `photo_planner/`.

A notebook is a file of cells (text + code) you run one at a time. It is a lab, not the final product.

## What you should complete in the notebook

1. Store the API key without committing it
2. `requests.get` to `/data/2.5/forecast` → print `status_code`
3. A function that returns forecast JSON for a city
4. Extract temperature, wind, clouds, rain chance (`pop`), sunset
5. Optional: a tiny plot of temperature across a few slots

Then copy the ideas into `photo_planner/` — do not keep the finished app only in the notebook.

## Google Colab

1. Upload the notebook, or open it from GitHub once the repo exists.
2. Do **not** hard-code the API key in a cell you will commit.
3. In Colab, prefer `userdata.get("OPENWEATHER_API_KEY")` or `getpass`.

## Local Jupyter

```bash
pip install -r ../requirements.txt jupyter
jupyter notebook 01_forecast_api_colab.ipynb
```
