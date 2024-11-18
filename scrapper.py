from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import random
from selenium_stealth import stealth

# Sets up the Chrome browser for us to use. Also adds some extra settings to make it work smoother!
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")  # Disables GPU stuff—helps prevent some random issues.
    chrome_options.add_argument("--no-sandbox")  # Sandbox? Nah, we don’t need it here.
    chrome_options.add_argument("--window-size=1920,1080")  # Makes the browser window full HD, perfect for scraping!
    service = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    apply_stealth_settings(driver)
    return driver

# Makes the browser less detectable so the website thinks it's a normal user, not a bot.
def apply_stealth_settings(driver):
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)

# Finds and clicks on the language dropdown, and then selects each language one by one.
def select_dropdown_language(driver, wait):
    dropdown = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#header_language_menu')))
    dropdown.click()
    # random_delay()

    # Waits until all the dropdown items show up, then clicks through each one.
    items = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'o-list-select__item')))
    actions = ActionChains(driver)

    for index, item in enumerate(items):
        if index == 0:
            continue  # Skips the first item—guess it's not what we need.
        actions.move_to_element(item).click().perform()
        # random_delay()

    # Hits the submit button to apply the selected language.
    submit_button = driver.find_element(By.XPATH, '//*[@id="header_language_menu"]/div[2]/form/div/button')
    submit_button.click()
    # random_delay()

# Keeps clicking "Load More" until we reach the bottom or there's no more content to load.
# Keeps clicking "Load More" until we reach the bottom or there's no more content to load.
# If iterations is set to None, it will keep going until the button disappears.
def load_more_content(driver, wait, iterations=None):
    count = 0  # Just to keep track of how many times we've clicked "Load More"
    
    while True:
        try:
            # Scroll to the bottom of the page to load more content.
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(2)  # Give the page a moment to load more stuff.
            driver.execute_script("window.scrollBy(0, -1000);")  # Scroll back up a bit to ensure the button is visible.
            # time.sleep(1)

            # Try to find and click the "Load More" button.
            load_more_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[2]/div[1]/div/main/section[1]/p/button'))
            )
            
            #Normal Click operation was being a problem for some reason. So I had to change the action to javascript click. 
            driver.execute_script("arguments[0].click();", load_more_button)
            # time.sleep(3)  # Wait a bit for new content to load.
            
            count += 1
            print(f"'Load More' clicked {count} times.")

            # If a specific number of iterations is provided, break out of the loop after reaching the count.
            if iterations is not None and count >= iterations:
                break

        except Exception as e:
            # If we can't find the "Load More" button, it probably means there's no more content to load.
            print(f"No more 'Load More' button found or error: {e}")
            break

# Grabs all the links to the songs from the list on the page.
def extract_song_links(driver):
    ol = driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div[1]/div/main/section[1]/section/ol')
    list_items = ol.find_elements(By.TAG_NAME, "li")
    links = []

    # Loop through each list item and try to find song links inside.
    for index, li in enumerate(list_items, start=1):
        try:
            a_tag = li.find_element(By.XPATH, ".//a[contains(@href, '/song/')]")
            href = str(a_tag.get_attribute("href"))
            links.append(href)
            print(f"Found href in <li> {index}: {href}")
        except Exception:
            print(f"No links found in <li> {index}")
    
    return links

# Checks if the given text mentions "Aditya Music". If yes, it means we got a match.
def process_text(text):
    pattern = r".*Aditya Music.*"
    if re.search(pattern, text):
        print("Match found!")
        return True
    else:
        print("No match found.")
        return False

# Takes a bunch of song links, checks each one to see if it's related to "Aditya Music", and counts the matches.
def count_songs_by_aditya_music(driver, links, wait, max_songs=None):
    song_count = 0
    i = 0
    while True:
        try:
            url = links[i]
            i = i + 1
            driver.get(url=url)
            # Waits for the <p> tag that tells us more about the song.
            p_tag = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div[2]/div[1]/div/main/div[2]/figure/figcaption/p[3]')
            ))
            p_text = p_tag.text
            song_count += 1 if process_text(p_text) else 0
            
            if max_songs is not None and i >= max_songs:
                i = i + 1
                break
        except IndexError as e:
            print("Index Out of Range. Probably iterated through all urls Or There were no links to begin with.")
            break

    print(f"Total number of songs associated with Aditya Music: {song_count}")
    return song_count

# A little delay function to make our actions seem more human and less like a robot.
def random_delay():
    time.sleep(random.uniform(2, 5))

# This is where everything comes together—runs the whole process.
def main():
    driver = initialize_driver()
    driver.get('https://www.jiosaavn.com/artist/s.-p.-balasubrahmanyam-songs/Ix5AC5h7LSg_')
    wait = WebDriverWait(driver, 10)

    select_dropdown_language(driver, wait)
    load_more_content(driver, wait)  # Adjust iterations if you want to load more songs for testing purposes. 2 is just for the testing purposes. Remove this so that it can run till max content.

    links = extract_song_links(driver)
    count_songs_by_aditya_music(driver, links, wait) #max_songs in this function for the testing purposes. You can Make it None so that this code runs through all the collected urls.
    print(count_songs_by_aditya_music)
    driver.quit()

# Start the script here.
if __name__ == "__main__":
    main()
