from nextcord.ext import commands
import nextcord
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

with open('users/allowed.json') as file:
  json_content = file.read()
  
allowed_ids = json.loads(json_content)


class Ausbildung(commands.Cog):

  def __init__(self, bot):
    self.client = bot

  @commands.command(description='Request To Get Emails From Ausbildung.de')
  async def aus(self, ctx, *, url):

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
    if "ausbildung" not in url or response.status_code != 200:
      await ctx.message.add_reaction("❌")
      await ctx.reply("Lien ghalat.")
      return

    await ctx.message.add_reaction("✅")
    message = await ctx.reply("Ok att.")
    open("on", "w").close()
    try:
      # Initialize driver
      options = Options()
      options.headless = True
      driver = webdriver.Firefox(options=options)
      driver.get(url)
      # Handle cookies
      try:
        cookie_button = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located(
            (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")))
        cookie_button.click()
      except:
        pass

      # Scrolling
      previous_height = driver.execute_script(
        "return document.body.scrollHeight")

      while True:
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        try:
          button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((
              By.XPATH,
              '//button[contains(@class, "btn-filled--light-grey") and contains(text(), "Weitere Ergebnisse laden")]'
            )))
          button.click()
        except:
          pass
        await message.edit(content="Searching for links...    ( / )")

        time.sleep(2)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == previous_height:
          break

        previous_height = new_height
        await message.edit(content="Searching for links...    ( \\ )")

      # Get page source
      page_source = driver.page_source
      driver.quit()

      soup = BeautifulSoup(page_source, 'html.parser')

      # Get links
      links = soup.find_all('a', class_='job-posting-cluster-cards__link')
      link_urls = [
        urljoin('https://www.ausbildung.de', link['href']) for link in links
      ]

      await message.edit(content=f"l9it {len(link_urls)} link.")
      time.sleep(2)
      # Get emails from links
      await message.edit(content="Searching for emails in each link page.")
      time.sleep(2)
      emails = []
      for i, link in tqdm(enumerate(link_urls)):
        await message.edit(content=f"({i+1}/{len(link_urls)})")
        response = requests.get(link)
        r = requests.get(link)
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        soup = BeautifulSoup(r.content, 'html.parser')
        extracted_emails = re.findall(email_regex, str(soup))

        emails.extend(extracted_emails)

      emails = [
        email for email in list(set(emails)) if "onlyfy.jobs" not in email
      ]

      await message.edit(content="chof prv.")

      # Save emails to text file
      file_path = f"result{user_id}.txt"
      with open(file_path, "w") as file:
        for email in emails:
          file.write(email + "\n")

      await ctx.author.send(files=[nextcord.File(file_path)])
    except:
      for file in [file_path, "geckodriver.log", "on"]:
        os.remove(file)

    for file in [file_path, "geckodriver.log", "on"]:
      os.remove(file)


def setup(bot):
  bot.add_cog(Ausbildung(bot))
