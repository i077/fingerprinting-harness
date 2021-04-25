import itertools
import json
from typing import Dict, List
from urllib.parse import urlparse
import typer


def main(
    file: str = typer.Option(
        "requests.json", help="Path to the JSON file of requests to analyze"
    )
):
    # Load in list of requests and trackers from Disconnect
    requests_by_site: Dict[str, List[dict]] = {}
    trackers: Dict[str, List[dict]] = {}
    with open(file, "r") as f:
        requests_by_site = json.load(f)
    with open("disconnect-tracking/services.json", "r") as f:
        trackers = json.load(f)["categories"]

    # Just looking at fingerprinters
    fingerprinters = trackers["FingerprintingInvasive"]

    # Each entry in a category of Disconnect's trackers dict is a list of single-key
    # dictionaries (why?), so union those and map each key to its domain.
    # That is, in each category,
    #   [{"Name": {"https://www.domain.com/": ["domain.com", ...], ...}}, ... ]
    #       ==> {"Name": ["domain", ...], ...}
    tracker_dict = {
        name: [domain for domains in val.values() for domain in domains]
        for name, val in {
            k: v for tracker in fingerprinters for k, v in tracker.items()
        }.items()
    }

    # Analyze each site
    for site, req_list in requests_by_site.items():
        tracker_list: List[str] = get_site_trackers(req_list, tracker_dict)
        typer.secho(f"{site} made {len(tracker_list)} requests to fingerprinters.")


def get_site_trackers(
    req_list: List[dict], trackers: Dict[str, List[str]]
) -> List[str]:
    """
    Given a list of requests (made from accessing a site) and a list of
    trackers (single-key dictionaries), return the list of trackers present
    in the list of requests.
    """
    # Filter for entries that are actually requests for resources
    resources = [r for r in req_list if r["entryType"] == "resource"]

    # For each request made, get its domain and check if it matches the domain of a tracker
    site_trackers: List[str] = []
    for request in resources:
        parsed_url = urlparse(request["name"])
        assert isinstance(parsed_url.hostname, str)
        # We check for substring instead of equality since hostnames can begin with 'www.'
        for tracker in [
            k
            for k, v in trackers.items()
            if any([domain in parsed_url.hostname for domain in v])
        ]:
            if tracker not in site_trackers:
                site_trackers.append(tracker)

    return site_trackers


if __name__ == "__main__":
    typer.run(main)
