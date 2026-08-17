"""Fetch mutual fund NAV data from MFapi.in and convert JSON data to CSV."""

from pathlib import Path
import requests
import pandas as pd

API_URL = "https://api.mfapi.in/mf/125497"
OUTPUT_FILE = Path(__file__).resolve().parent / "api_data.csv"


def fetch_nav_data() -> dict:
    """Call the public API and return the JSON response."""
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def convert_to_csv(payload: dict) -> None:
    """Convert the NAV records in the JSON response to a CSV file."""
    meta = payload.get("meta", {})
    records = payload.get("data", [])

    if not records:
        raise ValueError("No NAV records were returned by the API.")

    df = pd.DataFrame(records)

    df["scheme_code"] = meta.get("scheme_code")
    df["scheme_name"] = meta.get("scheme_name")
    df["fund_house"] = meta.get("fund_house")

    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

    df = df[
        ["scheme_code", "scheme_name", "fund_house", "date", "nav"]
    ].dropna(subset=["date", "nav"])

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"API status: {payload.get('status', 'UNKNOWN')}")
    print(f"Records saved: {len(df)}")
    print(f"CSV created: {OUTPUT_FILE}")


def main() -> None:
    """Run the API extraction workflow."""
    try:
        payload = fetch_nav_data()
        convert_to_csv(payload)
    except requests.RequestException as exc:
        print(f"API request failed: {exc}")
    except (ValueError, KeyError) as exc:
        print(f"Data processing failed: {exc}")


if __name__ == "__main__":
    main()
