import os
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.core.ports.driven.futures_basket_downloader import FuturesBasketDownloader


class EurexFuturesBasketDownloader(FuturesBasketDownloader):
    
    EUREX_URL = "https://www.eurex.com/ex-en/data/clearing-files/notified-deliverable-bonds-conversion-factors"
    BASE_URL = "https://www.eurex.com"

    def download(self, save_dir: str) -> str | None:
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            # Fetch the Eurex page
            response = requests.get(self.EUREX_URL, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # Find the download link
            target_link = None
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if (".xlsx" in href or ".csv" in href) and (
                    "notified" in href.lower() or "deliverable" in href.lower()
                ):
                    target_link = href
                    break

            if not target_link:
                print("No download link found on Eurex page")
                return None

            full_url = (
                target_link
                if target_link.startswith("http")
                else self.BASE_URL + target_link
            )

            # Determine file extension and create filename
            extension = ".xlsx" if ".xlsx" in full_url else ".csv"
            today_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{today_str}_deliverable_bonds{extension}"
            save_path = os.path.join(save_dir, filename)

            print(f"Downloading from: {full_url}")
            print(f"Saving to: {save_path}")

            # Download the file
            file_res = requests.get(full_url, headers=headers)
            file_res.raise_for_status()

            # Save to disk
            with open(save_path, "wb") as f:
                f.write(file_res.content)

            # Load into DataFrame
            if extension == ".xlsx":
                df = pd.read_excel(BytesIO(file_res.content))
            else:
                df = pd.read_csv(BytesIO(file_res.content), sep=None, engine="python")

            # Transform contract names: "CONTRACT SI YYYYMMDD PS" -> "CONTRACT YYYY-MM-DD"
            if "#Contract" in df.columns:
                df["#Contract"] = df["#Contract"].str.replace(
                    r"([A-Z]+)\s+SI\s+(\d{4})(\d{2})(\d{2})\s+PS",
                    r"\1 \2-\3-\4",
                    regex=True,
                )

            # Save the transformed CSV
            if extension == ".csv":
                df.to_csv(save_path, index=False, sep=";")
                csv_path = save_path
            else:
                # If original was xlsx, also save as CSV
                csv_path = save_path.replace(".xlsx", ".csv")
                df.to_csv(csv_path, index=False, sep=";")

            return csv_path

        except Exception as e:
            print(f"Error downloading from Eurex: {e}")
            return None
