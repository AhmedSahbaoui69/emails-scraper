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


class HotelCareer(commands.Cog):

  def __init__(self, bot):
    self.client = bot

  @commands.command(description='Request To Get Emails From hotelcareer.de')
  async def hotcar(self, ctx, *, url):

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
    if "https://www.hotelcareer.de/" not in url:
      await ctx.message.add_reaction("❌")
      await ctx.reply("Lien ghalat.")
      return

    await ctx.message.add_reaction("✅")
    message = await ctx.reply("Ok att.")
    open("on", "w").close()
    try:
      os.remove('emails.txt')
    except:
      pass
    open("emails.txt", "w").close()
    try:
      # Initialize driver
      options = Options()
      options.headless = False
      driver = webdriver.Firefox(options=options)
      driver.get(url)

      # Remove dialog
      try:
        close_button = WebDriverWait(driver, 60).until(
          EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[12]/div[1]/button")))
        close_button.click()
      except:
        pass

      # Get number of clicks required
      try:
        interations_element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div[4]/div/div[2]/div[2]/div[2]/ul/li[2]/span")))
        iterations = int(interations_element.get_attribute("innerHTML"))
      except:
        pass

      # Let us commence forth
      for i in range(iterations):
        await message.edit(content=f"Page ( {i+1} / {iterations} ).")
        # Wait for page to load
        while True:
          try:
            WebDriverWait(driver, 5).until(
              EC.presence_of_element_located(
                (By.CLASS_NAME, "logo")))
            break
          except:
            driver.refresh()
        # Get page source
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        # Get link elements
        links = soup.find_all('a', class_='job font-size-l link-blue-none')
        link_urls = [ urljoin('https://www.hotelcareer.de', link['href']) for link in links ]

        # Open a new tab
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        
        # Iterate links
        emails = []
        for j, link in enumerate(link_urls):
          await message.edit(content=f"Page ( {i+1} / {iterations} ). \n- Link ( {j+1} / {len(link_urls)} ).")
          try:
            # Open link
            driver.get(link)
            # Wait for page to load
            while True:
              try:
                WebDriverWait(driver, 5).until(
                  EC.presence_of_element_located(
                    (By.CLASS_NAME, "logo")))
                break
              except:
                driver.refresh()
            # Get page source
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            # Get emails
            email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            soup = BeautifulSoup(page_source, 'html.parser')
            extracted_emails = re.findall(email_regex, str(soup))
            # Extend list
            emails.extend(extracted_emails)
          except:
            pass

        # Switch to the old tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Save emails to a file
        emails = list(set(emails))
        with open('emails.txt', 'a') as file:
          for email in emails:
              file.write(email + '\n')

        # Next page
        try:
          close_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
              (By.XPATH, "/html/body/div[4]/div/div[2]/div[2]/div[2]/ul/li[2]/a[2]")))
          close_button.click()
        except:
          pass


    except Exception as e:
      for file in ["geckodriver.log", "on"]:
        try:
          os.remove(file)
        except:
          pass
      await ctx.channel.send("tra chi erreur smo7at.")
      print(e)

    for file in ["geckodriver.log", "on"]:
        try:
          os.remove(file)
        except:
          pass

def setup(bot):
  bot.add_cog(HotelCareer(bot))
