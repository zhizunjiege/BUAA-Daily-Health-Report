import argparse
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC, wait
from webdriver_manager.chrome import ChromeDriverManager


def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    options.add_argument('no-sandbox')
    service = Service(executable_path=ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    return browser


def login(browser, username, password, el_user, el_pwd, el_btn, el_loc):
    username_input = browser.find_element(By.XPATH, el_user)
    password_input = browser.find_element(By.XPATH, el_pwd)
    login_button = browser.find_element(By.XPATH, el_btn)
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()
    browser.implicitly_wait(5)
    # wait.WebDriverWait(browser, timeout=10).until(EC.visibility_of_element_located(el_loc))
    print(browser.title)
    print(browser.current_url)
    # TODO: check whether login succeeded or not

    return None


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
    print(browser.title)
    print(browser.current_url)
    location_button = browser.find_element(By.XPATH, el_loc)
    location_button.click()
    browser.implicitly_wait(5)
    # wait.WebDriverWait(browser, timeout=10).until(lambda: len(location_button.text) > 0)
    submit_button = browser.find_element(By.XPATH, el_sub)
    submit_button.click()
    browser.implicitly_wait(5)
    # wait.WebDriverWait(browser, timeout=10).until(EC.visibility_of_element_located(el_con))
    # confirm_button = browser.find_element(By.XPATH, el_con)
    # confirm_button.click()
    # wait.WebDriverWait(browser, timeout=10).until_not(EC.element_to_be_clickable(submit_button))

    # TODO: check whether report succeeded or not

    return None


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

    print(str(opt.latitude).split('.'))

    print('loading meta data...')
    with open('meta.json', 'r') as fp:
        meta = json.load(fp)
    print('meta data is: ', meta)

    attempts = 0
    while attempts <= opt.max_attempts:
        attempts += 1
        print('-' * 20 + f'the {attempts:3} th attempt' + '-' * 20)

        browser = driver()

        print('open login page...')
        try:
            browser.get(meta['url']['login'])
        except Exception:
            print('network error!')
            continue
        print('login page opened')

        print('login into system...')
        msg = login(
            browser,
            opt.username,
            opt.password,
            meta['el']['username'],
            meta['el']['password'],
            meta['el']['login_btn'],
            meta['el']['location_button'],
        )
        if msg:
            print('login failed: ', msg)
            continue
        print('login succeeded')

        print('open report page...')
        try:
            browser.get(meta['url']['report'])
        except Exception:
            print('network error!')
            continue
        print('report page opened')

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
