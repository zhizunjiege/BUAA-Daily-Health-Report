import argparse
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC, wait
from webdriver_manager.chrome import ChromeDriverManager


def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument('no-sandbox')
    service = Service(executable_path=ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    return browser


def login(browser, username, password, el_user, el_pwd, el_btn):
    username_input = browser.find_element(By.XPATH, el_user)
    password_input = browser.find_element(By.XPATH, el_pwd)
    login_button = browser.find_element(By.XPATH, el_btn)
    username_input.send_keys(username)
    password_input.send_keys(password)
    print(username)
    print(password)
    login_button.click()
    wait.WebDriverWait(browser, timeout=10).until(EC.url_contains('buaaStudentNcov'))
    # title_contains('北航师生报平安系统')

    # TODO: check whether login succeeded or not

    return ''


def report(browser, longitude, latitude, el_loc, el_sub, el_con):
    js_code = f'''
window.navigator.geolocation.getCurrentPosition = function (success) {{
  let position = {{
    coords: {{
      longitude: "{longitude}",
      latitude: "{latitude}",
    }},
  }};
  success(position);
}};
    '''
    browser.execute_script(js_code)
    # browser.implicitly_wait(1)  # or time.sleep?

    location_button = browser.find_element(By.XPATH, el_loc)
    submit_button = browser.find_element(By.XPATH, el_sub)
    confirm_button = browser.find_element(By.XPATH, el_con)
    location_button.click()
    wait.WebDriverWait(browser, timeout=10).until(lambda: len(location_button.text))
    submit_button.click()
    wait.WebDriverWait(browser, timeout=10).until(EC.visibility_of(confirm_button))
    # confirm_button.click()
    # wait.WebDriverWait(browser, timeout=10).until_not(EC.element_to_be_clickable(submit_button))

    # TODO: check whether report succeeded or not

    return ''


if __name__ == "__main__":
    print('parsing options...')
    parser = argparse.ArgumentParser(description='Automatically finish daily healy report for buaaers.')
    parser.add_argument('--username', '-u', type=str, help='username of uniform authentication account')
    parser.add_argument('--password', '-p', type=str, help='username of uniform authentication account')
    parser.add_argument('--longitude', '-o', type=float, help='longitude of report location')
    parser.add_argument('--latitude', '-a', type=float, help='latitude of report location')
    parser.add_argument('--max-attempts', '-m', type=int, default=3, help='max times of attempts when report failed')
    opt = parser.parse_args()
    print('options are: ', opt)

    print('loading meta data...')
    with open('meta.json', 'r') as fp:
        meta = json.load(fp)
    print('meta data is: ', meta)

    attempts = 0
    while attempts <= opt.max_attempts:
        attempts += 1
        print('-' * 20 + f'the {attempts:3} th attempt' + '-' * 20)

        print('open browser...')
        browser = driver()
        try:
            browser.get(meta['url'])
        except Exception:
            print('network error!')
            continue
        print('browser opened')

        print('login into system...')
        msg = login(
            browser,
            opt.username,
            opt.password,
            meta['el']['username'],
            meta['el']['password'],
            meta['el']['login_btn'],
        )
        if msg:
            print('login failed: ', msg)
            continue
        print('login succeeded')

        print('start reporting...')
        msg = report(
            browser,
            opt.longitude,
            opt.latitude,
            meta['el']['location_button'],
            meta['el']['submit_button'],
            meta['el']['confirm_button'],
        )
        if msg:
            print('report failed: ', msg)
            continue
        print('report succeeded')

        break

    print('task finished successfully!')
