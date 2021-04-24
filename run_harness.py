import json
from typing import Dict, List
import typer
from selenium.webdriver import Firefox, FirefoxOptions

GET_REQ_JS = """
var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;
"""


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
    requests_by_site: Dict[str, List] = {}
    with open("sites.txt", "r") as f:
        lines = f.readlines()
        sites = [l.strip() for l in lines]
    typer.secho(f"Found {len(sites)} site(s) to read.")

    # Get list of requests for each site
    for site in sites:
        requests_by_site[site] = visit_site(driver, site)
    typer.secho("Closing browser.")
    driver.close()

    # Save lists to a JSON file
    with open("requests.json", "w") as f:
        json.dump(requests_by_site, f)


def visit_site(driver: Firefox, url: str):
    """
    Visit a site and log the requests the browser makes during the page load.
    Returns a list of requests made.
    """
    typer.secho(f"Visiting {url}...")
    driver.get(url)
    requests_list: list = driver.execute_script(GET_REQ_JS)
    return requests_list


if __name__ == "__main__":
    typer.run(main)
