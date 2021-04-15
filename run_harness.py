from typing import List
import typer
from selenium.webdriver import Firefox, FirefoxOptions


def main(
    headless: bool = typer.Option(True, help="Whether to run the browser headlessly")
):
    # Initialize browser
    typer.secho("Initializing browser...")
    browser_opts = FirefoxOptions()
    browser_opts.headless = headless
    driver = Firefox(options=browser_opts)
    driver.set_window_size(1920, 1080)

    # Get list of sites
    sites: List[str]
    with open("sites.txt", "r") as f:
        lines = f.readlines()
        sites = [l.strip() for l in lines]
    typer.secho(f"Found {len(sites)} site(s) to read.")


if __name__ == "__main__":
    typer.run(main)
