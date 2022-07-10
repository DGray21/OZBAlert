# OZBAlert (Ozbargain Alert)

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import re
import time
import feedparser
from datetime import datetime

from playsound import playsound
from colorama import init
from colorama import Fore, Back, Style
from os import system

rssUrl = 'https://www.ozbargain.com.au/deals/feed'  #OZB rss feed url
maxPrice = 1.00
minPrice = 0.01
interval = 5

blockedCats = []

def PrintHeader():
    # CHange header title
    system("title OzBargain Price Alert")
    # Display the header text
    print('┌───────────────────────┐')
    print('│' + Fore.WHITE + ' OzBargain Price Alert ' + Fore.RESET + '│')
    print('└───────────────────────┘', end='\n\n')
    print('Press Ctrl+C to exit', end='\n\n')

def ChangeTitle():
    system("title OzBargain Price Alert - Min: $" + "{:.2f}".format(minPrice) + " Max: $" + "{:.2f}".format(maxPrice))

def GetInput():
    global maxPrice
    global minPrice
    global interval
    pricesFound = False
    timeSet = False
    while not pricesFound:
        try:
            print('Maximum price value (in dollars):')
            maxPrice = float(input())
        except:
            continue

        try:
            print('Minimum price value (in dollars):')
            minPrice = float(input())
        except:
            continue

        if minPrice >= maxPrice:
            print(Fore.RED + 'Min price higher than max price!' + Fore.RESET)
            continue

        if minPrice < 0.01:
            print(Fore.RED + 'Min price too low! (Below 1¢)' + Fore.RESET)
            print('To access freebies go to: https://www.ozbargain.com.au/freebies')
            continue
        pricesFound = True

    while not timeSet:
        try:
            print('Set update interval time (in minutes):')
            interval = int(input()) * 60
        except:
            continue
        timeSet = True



def AlertLoop(url,alertFile):
    pastIds = []
    alertRunning = True
    priceRegex = r'(\$\d+\,\d{3})|(\$\d+\.\d\d)|(\$\d+)'
    print('Price Alert running...')
    print(f'Looking for prices between ${"{:.2f}".format(minPrice)} and ${"{:.2f}".format(maxPrice)}.')
    print(f'Interval between updates is {int(interval / 60)} minute(s)', end='\n\n')

    while alertRunning:
        # Get the feed again
        feed = feedparser.parse(url)
        # Loop through each item in the feed
        for entry in feed.entries:

            match = re.search(priceRegex, entry.title)
            if match is not None:
                price = 0.0
                # If a item is found within the price range
                try:
                    price = float(str(match.group())[1:].replace(',', ''))
                except:
                    continue

                if (price > minPrice) and (price < maxPrice):
                    # Loop through past ID's to prevent duplicate entries from showing up
                    guid = entry.id[:6] # Parse ID from the feed
                    idFound = False
                    for idItem in pastIds:  # Loop through to see if the id exists
                        if idItem == guid:
                            idFound = True
                            break

                    if not idFound:
                        # First check if this item is on the block list
                        isBlocked = False
                        if len(blockedCats) > 0:
                            for blocked in blockedCats:
                                if entry.tags[0]['term'].replace(r'&amp;', '&') in blocked:
                                    isBlocked = True
                                    break

                        # If not blocked give an alert
                        if not isBlocked:
                            # Print the alert information
                            curTime = datetime.now().strftime('%d-%m-%Y - %I:%M %p')
                            created = entry.published_parsed
                            print(Fore.YELLOW + f'Deal found! ({curTime})')
                            print(Fore.WHITE + entry.title + Fore.RESET)

                            print('Price: ' + Fore.GREEN + '$' + '{:.2f}'.format(price) + Fore.RESET)
                            print('Link: ' + Fore.CYAN + entry.link + Fore.RESET)
                            print('Category: ' + entry.tags[0]['term'].replace(r'&amp;', '&'))
                            # Publish date
                            print(f'Created (GMT): {created[2]}-{created [1]}-{created[0]} at ' +
                                  f'{created[3]}:{str(created[4]).zfill(2)}', end='\n\n')

                            pastIds.append(entry.id[:6])    # store the ID the remove duplicates

                            # Play alert sound
                            playsound(alertFile)
                            time.sleep(2)

        # Wait the interval
        time.sleep(interval)

def LoadBlockList(filename):
    global blockedCats
    print('Loading block list...', end='')
    file = open(filename, 'r')
    for item in file.readlines():
        # Remove misc HTML formatting
        blockedCats.append(item.replace(r'&amp;', '&'))

    print('loaded ' + str(len(blockedCats)) + ' blocked categories')

    if len(blockedCats) == 0:
        print('Empty block list - no categories blocked')
    file.close()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    init()          # Start Colorama for fancy coloured output
    PrintHeader()
    LoadBlockList('block.txt')
    GetInput()
    ChangeTitle()
    AlertLoop(rssUrl, 'alert.wav')



