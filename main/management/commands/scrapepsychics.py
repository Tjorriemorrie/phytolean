import main.constants as c
import time
import logging
from typing import List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from unidecode import unidecode

from main.models import Psychic, Role, Status
from main.selectors import update_psychics_stats

logger = logging.getLogger(__name__)

BASE_URL = "https://www.sa-psychics.com"
START_URL = f"{BASE_URL}/psychic-reading"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:140.0) Gecko/20100101 Firefox/140.0",
}


from urllib.parse import urljoin


def parse_advisors(fragment: str) -> List[Psychic]:
    psychics = []
    soup = BeautifulSoup(fragment, "lxml")

    for card in soup.select("h3"):
        name = card.get_text(strip=True)
        container = card.find_parent("div", class_="psychicItem") or card.parent

        # Roles
        role_tag = container.select_one("div.specialization ul.spec-list li a")
        if role_tag:
            raw_role = role_tag.get_text(strip=True)
            role_names = []
            for part in raw_role.split("|"):
                part = part.strip()
                if part.startswith("Psychic "):
                    part = part[len("Psychic "):]
                role_names.append(part)
        else:
            role_names = []

        # Tagline
        bio_tag = container.find("p", class_="tagline")
        bio = bio_tag.get_text(strip=True) if bio_tag else ""

        # Profile URL
        link_tag = card.find("a", href=True)
        url = urljoin("https://www.sa-psychics.com", link_tag["href"]) if link_tag else ""

        # Image URL
        img_tag = container.select_one("img.company_logo")
        img = urljoin("https://www.sa-psychics.com", img_tag["src"]) if img_tag else ""

        # Status
        status = ""
        for status_id in ["online", "oncall", "offline"]:
            status_span = container.select_one(f"span[id^={status_id}]")
            if status_span and "display:inline" in status_span.get("style", ""):
                status = status_span.get_text(strip=True).title()
                break

        # Get or create the Psychic
        psychic, created = Psychic.objects.update_or_create(
            url=url,
            defaults={
                "name": name,
                "tagline": bio,
                "img": img,
            },
        )
        psychics.append(psychic)

        # Update roles
        roles = []
        for role_name in role_names:
            role_obj, _ = Role.objects.get_or_create(name=role_name)
            roles.append(role_obj)
        psychic.roles.set(roles)

        # Save status (one per scrape)
        if status:
            status_ins = Status.objects.create(
                psychic=psychic,
                status=status,
                status_at=now()
            )
            if status_ins.status == c.PSYCHIC_STATUS_ONLINE:
                psychic.last_online_at = now()
            elif status_ins.status == c.PSYCHIC_STATUS_ONCALL:
                psychic.last_oncall_at = now()
            psychic.save()

        logger.info(
            unidecode(
                f"{psychic.name:<20} | {', '.join(role_names):<30} | {status:<7} | {psychic.tagline} | {psychic.url} | {psychic.img}"
            )
        )
    return psychics


def find_loadmore_endpoint(soup: BeautifulSoup) -> Optional[Tuple[str, int, int]]:
    """
    Find the AJAX endpoint and pagination info from the 'See More Advisors' button.
    """
    btn = soup.find("a", string=lambda s: s and "See More Advisors" in s)
    if not btn:
        return None

    ajax_url = btn.get("data-url") or btn.get("href") or ""
    if not ajax_url:
        return None

    ajax_url = urljoin(BASE_URL, ajax_url.lstrip("/"))
    offset = int(btn.get("data-offset", 0))
    limit = int(btn.get("data-limit", 24))
    return ajax_url, offset, limit


def scrape_all() -> List[Psychic]:
    """
    Scrape all advisor pages, logging info along the way.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    response = session.get(START_URL, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    advisors = parse_advisors(response.text)

    more = find_loadmore_endpoint(soup)
    while more:
        ajax_url, offset, limit = more
        payload = {"offset": offset, "limit": limit}

        resp = session.post(ajax_url, data=payload, timeout=30)
        if resp.status_code != 200 or not resp.text.strip():
            break

        new_advisors = parse_advisors(resp.text)
        if not new_advisors:
            break

        advisors.extend(new_advisors)
        logger.info(f"Fetched {len(new_advisors)} more advisors (total: {len(advisors)})")

        offset += limit
        more = (ajax_url, offset, limit)
        time.sleep(1)

    return advisors


class Command(BaseCommand):
    help = "Scrape psychic advisors from sa-psychics.com"

    def handle(self, *args, **options):
        logger.info("Starting SA-Psychics advisor scrape...")
        advisors = scrape_all()
        logger.info(f"Scraping complete. Total advisors scraped: {len(advisors)}")

        logger.info("Starting SA-Psychics stats update...")
        update_psychics_stats()
        logger.info('Stats update complete for psychics')
