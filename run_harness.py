import json
from typing import Dict, List
import typer
from selenium.webdriver import Firefox, FirefoxOptions
from threading import Thread

GET_REQ_JS = """
var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;
"""

# Yes, this is a global. Needed for use by multiple threads.
requests_by_site: Dict[str, List] = {}


def main(
    headless: bool = typer.Option(True, help="Whether to run the browser headlessly"),
    threads: int = typer.Option(1, help="How many concurrent browsers to use"),
    sites_path: str = typer.Option("sites.txt", help="Path to list of sites to use"),
    out_path: str = typer.Option(
        "requests.json", help="Path to write requests json to"
    ),
):
    # Get list of sites & divide up for each thread
    sites: List[str]
    with open(sites_path, "r") as f:
        lines = f.readlines()
        sites = [l.strip() for l in lines]
    typer.secho(f"Found {len(sites)} site(s) to visit.")

    runners: List[Runner] = []
    for i in range(threads):
        runner = Runner(site_list=sites[i::threads], headless=headless)
        runner.thread.start()
        runners.append(runner)

    # Wait for all threads to finish
    for runner in runners:
        if runner.thread.is_alive:
            runner.thread.join(60)

        # Save lists to a JSON file every so often
        with open(out_path, "w") as f:
            json.dump(requests_by_site, f)
        with open(out_path, "r") as f:
            t = json.load(f)
            typer.secho(f"Saved progress: {len(t)}/{len(sites)} visited.")


# Class to hold and run a browser instance. Used for threading
class Runner:
    def __init__(self, site_list: List[str], headless: bool):
        self.site_list = site_list

        # Initialize browser
        browser_opts = FirefoxOptions()
        browser_opts.headless = headless
        self.driver = Firefox(options=browser_opts)
        self.driver.set_window_size(1920, 1080)

        self.thread = Thread(target=self.open_sites)

    def log(self, msg: str):
        typer.secho(f"{self.thread.name}: {msg}")

    def open_sites(self):
        # Get list of requests for each site
        for idx, site in enumerate(self.site_list):
            self.log(f"Visiting {site} ({idx+1}/{len(self.site_list)})")
            requests_list: list = []

            try:
                # Visit the site!
                self.driver.get(site)
                requests_list: list = self.driver.execute_script(GET_REQ_JS)
            except Exception as e:
                self.log(f"Error when visiting {site}: {e}")

            requests_by_site[site] = requests_list
        self.log("Closing browser.")
        self.driver.close()


if __name__ == "__main__":
    typer.run(main)
