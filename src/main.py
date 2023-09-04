from typing import List, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import ElementClickInterceptedException
from config.base import env
from db.database import Session, engine
from api.geolocation import get_geolocation
import db.schema as schema
from sqlalchemy.dialects.postgresql import insert
from datetime import date
import re
from tqdm import tqdm


def extract_float(text: str) -> float:
    value = re.search(r"(\d+\.\d+|\d+)", text)
    return float(value.group(1))


def extract_integer(text: str) -> int:
    return int("".join(filter(str.isdigit, text)))


def split_address(address):
    city_state, zip_code = address.rsplit(" ", 1)
    city, state = city_state.rsplit(",", 1)

    return city.strip(), state.strip(), zip_code.strip()


def is_inside_safe_zone(element) -> bool:
    elem_x = element.location["x"]
    elem_y = element.location["y"]
    container: List[WebElement] = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "search-map-container"))
    )
    x = container[0].location["x"]
    y = container[0].location["y"]
    left_boundary = x + 180
    right_boundary = x + 1000 + 180
    top_boundary = y + 120
    bottom_boundary = y + 790 + 120
    return (
        left_boundary < elem_x < right_boundary
        and top_boundary < elem_y < bottom_boundary
    )


def get_markers() -> List[WebElement]:
    markers: List[WebElement] = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "custom-pin-image"))
    )
    filtered_markers: List[WebElement] = list(filter(is_inside_safe_zone, markers))
    sorted_markers: List[WebElement] = sorted(
        filtered_markers,
        key=lambda marker: (marker.location["y"], marker.location["x"]),
    )
    return sorted_markers


def scape(
    markers: List[WebElement], driver: WebDriver
) -> Tuple[list[schema.HouseListing], list[schema.PriceListing]]:
    houses: list[schema.HouseListing] = []
    pricing: list[schema.PriceListing] = []
    for marker in tqdm(markers):
        try:
            marker.click()
            wait = WebDriverWait(driver, 10)
            info = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "top-line-container")
                )
            )
            info: WebElement = info[0]
            try:
                specs: List[WebElement] = info.find_elements(
                    By.CLASS_NAME, "property-info-container"
                )
                children: List[WebElement] = specs[0].find_elements(By.TAG_NAME, "li")
                city, state, zip_code = split_address(
                    info.find_element(By.CLASS_NAME, "property-city-state-zip").text
                )
                address = info.find_element(By.CLASS_NAME, "property-address").text
                if children != []:
                    longitude, latitude = get_geolocation(
                        address, city, state, zip_code
                    )
                    houses.append(
                        schema.HouseListing(
                            address=address,
                            city=city,
                            state=state,
                            zip=zip_code,
                            beds=extract_integer(children[0].text),
                            baths=extract_float(children[1].text),
                            sqft=extract_integer(children[2].text),
                            longitude=longitude,
                            latitude=latitude,
                        )
                    )
                    pricing.append(
                        schema.PriceListing(
                            address=info.find_element(
                                By.CLASS_NAME, "property-address"
                            ).text,
                            city=city,
                            state=state,
                            zip=zip_code,
                            price=extract_integer(
                                info.find_element(By.CLASS_NAME, "property-price").text
                            ),
                            date=date.today(),
                        )
                    )
            except Exception as e:
                continue
        except ElementClickInterceptedException:
            continue
    return houses, pricing


def insert_data(
    houses: list[schema.HouseListing], pricing: list[schema.PriceListing]
) -> None:
    schema.Base.metadata.create_all(bind=engine)
    session = Session()
    house_dicts = [
        {
            key: value
            for key, value in house.__dict__.items()
            if not key.startswith("_sa_")
        }
        for house in houses
    ]
    stmt_house = (
        insert(schema.HouseListing)
        .values(house_dicts)
        .on_conflict_do_nothing(index_elements=["address", "city", "state", "zip"])
    )
    price_dicts = [
        {
            key: value
            for key, value in price.__dict__.items()
            if not key.startswith("_sa_")
        }
        for price in pricing
    ]
    stmt_pricing = (
        insert(schema.PriceListing)
        .values(price_dicts)
        .on_conflict_do_nothing(
            index_elements=["address", "city", "state", "zip", "date"]
        )
    )

    try:
        session.execute(stmt_house)
        session.execute(stmt_pricing)
        session.commit()
    except Exception as e:
        print(e)
    finally:
        session.close()


options = Options()
options.add_experimental_option("detach", True)
# options.add_argument("--headless")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
for url in env.SCRAPE_URLS.split(","):
    driver.get(url)
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)
    markers = get_markers()
    houses, pricing = scape(markers, driver)
    insert_data(houses, pricing)
driver.quit()
