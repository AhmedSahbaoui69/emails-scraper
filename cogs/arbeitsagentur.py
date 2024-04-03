from nextcord.ext import commands
import nextcord
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from urllib.parse import urljoin
import re
import requests
import time
from tqdm import tqdm
import json
import os
import asyncio

with open('users/allowed.json') as file:
  json_content = file.read()
allowed_ids = json.loads(json_content)


class Arbeitsagentur(commands.Cog):

  def __init__(self, bot):
    self.client = bot

  @commands.command(description='Request To Get Emails From Arbeitsagentur.de')
  async def arb(self, ctx, *, url):

    user_id = str(ctx.author.id)

    # Check if user is registered
    if user_id not in allowed_ids:
      await ctx.message.add_reaction("❌")
      await ctx.reply("Khoya ma3ndkch permission hh.")
      return

    if os.path.exists("on"):
      await ctx.reply("Khoya tsena nobtk hh.")
      return

    # Check if url is valid
    try:
      response = requests.get(url)
    except requests.exceptions.RequestException:
      pass
    if "arbeitsagentur" not in url or response.status_code != 200:
      await ctx.message.add_reaction("❌")
      await ctx.reply("Lien ghalat.")
      return

    await ctx.message.add_reaction("✅")
    message = await ctx.reply("Ok att.")
    open("on", "w").close()

    # Initialize driver
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)

    # Accept cookies
    while True:
      try:
        WebDriverWait(driver, 15).until(
          EC.text_to_be_present_in_element((By.TAG_NAME, "body"),
                                           "Alle zulassen"))
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
      except:
        break

    await message.edit(content="Cookies Accepted.")
    time.sleep(2)

    # Scrolling
    with open(f"links{user_id}.txt", "a") as file:
      await message.edit(content="Scrolling......    ( / )")
      while True:
        try:
          show_more_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
              (By.ID, "ergebnisliste-ladeweitere-button")))
          driver.execute_script("arguments[0].scrollIntoView();",
                                show_more_button)
          show_more_button.click()
          time.sleep(2)
          soup = BeautifulSoup(driver.page_source, "html.parser")
          last_index = soup.find_all(class_="ergebnisliste-item")[-1].find(class_="mitte-links-index").string
          await message.edit(last_index)
        except:
          pass

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all(class_="ergebnisliste-item")
        for item in items:
          inner_item = item.find(
            class_="mitte-links-titel color-red ba-link-icon ba-icon-linkout")
          if not inner_item:
            file.write(str(item["href"]) + "\n")

        # Delete ergebnisliste-item elements to free up ram
        driver.execute_script("document.querySelectorAll('.ergebnisliste-item').forEach(item => item.remove());")
        driver.execute_script("document.querySelectorAll('.page-divider').forEach(item => item.remove());")
        driver.execute_script("document.querySelectorAll('li').forEach(item => item.remove());")
        
        # If scrolling button no longer present
        try:
          driver.find_element(By.ID, "ergebnisliste-ladeweitere-button")
        except NoSuchElementException:
          break

    driver.quit()

    links = []
    with open(f"links{user_id}.txt", 'r') as file:
        for line in file:
            links.append(line.strip())

    await message.edit(content="Gathering elements...")

    driver = webdriver.Firefox(options=options)
    # Gathering email
    emails = []
    for i, link in tqdm(enumerate(links)):
      await message.edit(content=f"({i+1}/{len(links)})")
      try:
        driver.get(link)
      except:
        continue
      # Accept cookies
      if link == links[0]:
        try:
          WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"),
                                              "Alle zulassen"))
          driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
        except:
          pass

      # Check if captcha image is present
      try:
        actions = ActionChains(driver)
        actions.move_to_element(
          driver.find_element(By.ID, 'jobdetails-kontaktdaten-block'))
        WebDriverWait(driver, 2).until(
          EC.presence_of_element_located(
            (By.ID, "kontaktdaten-captcha-image")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image_url = soup.find(id="kontaktdaten-captcha-image")["src"]

        # Save Captcha image locally
        img_data = requests.get(image_url).content
        with open('captcha.jpg', 'wb') as f:
          f.write(img_data)

        # Send Captcha image
        cap = await ctx.send(files=[nextcord.File('captcha.jpg')])

        # Input the solution
        try:
          captcha_input = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(
              (By.ID, "kontaktdaten-captcha-input")))

          # Wait for user response
          def is_them(m):
            return True

          try:
            response = await self.client.wait_for('message',
                                                  check=is_them,
                                                  timeout=60.0)
          except asyncio.TimeoutError:
            await ctx.send('majawbtich.')

          # Enter response
          captcha_input.send_keys(response.content)
          driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
          time.sleep(2)
          # delete the interaction
          await cap.delete()
          await response.delete()
        except:
          pass

      except:
        pass

      # Get emails
      email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
      soup = BeautifulSoup(driver.page_source, 'html.parser')
      extracted_emails = re.findall(email_regex, str(soup))

      emails.extend(extracted_emails)

    driver.quit()

    emails = [
      email for email in list(set(emails)) if "onlyfy.jobs" not in email
    ]

    await message.edit(content="chof prv.")

    # Save emails to text file
    file_path = f"result{user_id}.txt"
    with open(file_path, "w") as file:
      for email in emails:
        if email == emails[0]:
          querry = re.search(r"(?<=was=)[^&]+", url).group(0).replace("%2F", "/").replace("%2D", "-")
          file.write("Search:  " + str(querry) + "\n")
          file.write(f"Total:  {len(emails)}" + "\n" + "\n")
        file.write(email + "\n")

    await ctx.author.send(files=[nextcord.File(file_path)])

    for file in ["geckodriver.log", "on", "captcha.jpg"]:
      os.remove(file)


def setup(bot):
  bot.add_cog(Arbeitsagentur(bot))
