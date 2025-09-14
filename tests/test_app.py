import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # noqa: F401 (kept for readability)
from app import app as dash_app


def test_header_present(dash_duo):
    dash_duo.start_server(dash_app)
    h1 = dash_duo.wait_for_element("h1.title", timeout=10)
    assert "Pink Morsel" in h1.text


def test_graph_renders(dash_duo):
    dash_duo.start_server(dash_app)
    dash_duo.wait_for_element("#sales-chart", timeout=10)
    svg = dash_duo.wait_for_element("#sales-chart .main-svg", timeout=10)
    assert svg is not None
    assert dash_duo.get_logs() == []


def test_region_picker_present_and_selectable(dash_duo):
    dash_duo.start_server(dash_app)

    # radio group present
    dash_duo.wait_for_element("#region-radio", timeout=10)

    # collect labels & inputs (same order)
    labels = dash_duo.driver.find_elements(By.CSS_SELECTOR, "#region-radio label")
    inputs = dash_duo.driver.find_elements(By.CSS_SELECTOR, '#region-radio input[type="radio"]')
    assert len(labels) == 5 and len(inputs) == 5

    # click the "North" label by index
    idx = next(i for i, lab in enumerate(labels) if lab.text.strip().lower() == "north")
    labels[idx].click()

    # wait until corresponding input becomes selected
    wait = WebDriverWait(dash_duo.driver, 5)
    wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, '#region-radio input[type="radio"]')[idx].is_selected())

    # assert selected
    refreshed_inputs = dash_duo.driver.find_elements(By.CSS_SELECTOR, '#region-radio input[type="radio"]')
    assert refreshed_inputs[idx].is_selected()
