import argparse
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC, wait
from webdriver_manager.chrome import ChromeDriverManager


def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    service = Service(executable_path=ChromeDriverManager(log_level=0).install())
    browser = webdriver.Chrome(service=service, options=options)
    return browser


# import argparse
# import json
# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.edge.service import Service
# from webdriver_manager.microsoft import EdgeChromiumDriverManager

# def driver():
#     service = Service(executable_path=EdgeChromiumDriverManager(log_level=0).install())
#     browser = webdriver.Edge(service=service)
#     return browser


def login(browser, username, password, el_user, el_pwd, el_btn):
    username_input = browser.find_element(By.XPATH, el_user)
    password_input = browser.find_element(By.XPATH, el_pwd)
    login_button = browser.find_element(By.XPATH, el_btn)
    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()
    time.sleep(3)
    # wait.WebDriverWait(browser, 5).until(EC.title_contains('个人中心'))


def check(browser, el_sub, txt):
    text = browser.find_element(By.XPATH, el_sub).get_attribute('text')
    for key in txt:
        if text == txt[key]:
            return key, text
    return None, text


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
    location_button = browser.find_element(By.XPATH, el_loc)
    location_button.click()
    time.sleep(2)
    # wait.WebDriverWait(browser, 5).until(lambda _: location_button.get_attribute('value'))
    submit_button = browser.find_element(By.XPATH, el_sub)
    submit_button.click()
    time.sleep(2)
    confirm_button = browser.find_element(By.XPATH, el_con)
    confirm_button.click()
    time.sleep(2)
    # wait.WebDriverWait(browser, 5).until(EC.visibility_of_element_located([By.XPATH, el_con]))
    # wait.WebDriverWait(browser, 5).until_not(EC.element_to_be_clickable(submit_button))


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

    with open('meta.json', 'r', encoding="utf8") as fp:
        meta = json.load(fp)
    print('meta data is: ', meta)

    attempts = 0
    while attempts < opt.max_attempts:
        print('-' * 20 + f'the {attempts+1:3} th attempt' + '-' * 20)

        browser = driver()
        browser.implicitly_wait(30)

        try:
            print('open login page...')
            browser.get(meta['url']['login'])
            print(browser.title, browser.current_url)
            print('login page opened')

            print('login into system...')
            login(
                browser,
                opt.username,
                opt.password,
                meta['el']['username_input'],
                meta['el']['password_input'],
                meta['el']['login_btn'],
            )
            print('login succeeded')

            print('open report page...')
            browser.get(meta['url']['report'])
            print(browser.title, browser.current_url)
            print('report page opened')

            time.sleep(2)

            print('check report status...')
            status, text = check(
                browser,
                meta['el']['submit_button'],
                meta['txt'],
            )
            print(status, text)
            if status == "allowed":
                print('report allowed')
            elif status == "reported":
                print('reported and will quit the script')
                break
            elif status == "disallowed":
                raise Exception('report disallowed and will try again')
            else:
                raise Exception('unknown status!')

            print('start reporting...')
            report(
                browser,
                opt.longitude,
                opt.latitude,
                meta['el']['location_button'],
                meta['el']['submit_button'],
                meta['el']['confirm_button'],
            )
            print('report succeeded')
            break
        except Exception as e:
            print(e)
            attempts += 1
            continue

    if attempts < opt.max_attempts:
        print('task finished successfully!')
    else:
        raise Exception('task failed!')
