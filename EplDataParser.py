import xlwt
import httplib2
import urllib.request as urlreq
import urllib
import time
from xlwt import Workbook
from bs4 import BeautifulSoup, SoupStrainer

class Parser:
    def __init__(self, webUrl):
        self.webUrl = webUrl
        
        
    def get_page(self, url):
        page = urlreq.urlopen(url).read()
        return page.decode("windows-1252")
    
    
    # Parse results of a given season and write to excel file
    def parse_results(self, page, rowName, teamname, row, sheet):
        points   = 0
        col      = 0
        lines    = page.splitlines()

        # Write the season name in first row
        sheet.write(row, col, rowName)
        col += 1

        # Find the columns corresponding to data we are interested in
        legend = lines[0].split(",")
        hIdx   = legend.index("HomeTeam")
        aIdx   = legend.index("AwayTeam")
        rIdx   = legend.index("FTR")
        
        # Process all games of a season
        for line in lines:
            arr = line.split(",");
            home = arr[hIdx].strip()
            away = arr[aIdx].strip()
            res  = arr[rIdx].strip()

            # We are only interested in results of 'teamname'
            if home != teamname and away != teamname:
              continue;

            if home == teamname and res == "H":
              points += 3 # Won a home game
            elif away == teamname and res == "A":
              points += 3 # Won an away game
            elif res == "D":
              points += 1 # Drew the game
            sheet.write(row, col, points)
            col += 1 # (Row, Col) -> (Season, Game)
        
        
    # Parse fouls data of a given season and write to excel file
    def parse_fouls(self, page, rowName, teamname, row, sheet, offset):
        lines   = page.splitlines()
        legend  = lines[0].split(",")
        
        # Only .csv files from 00/01 have stats
        if "HF" in legend :
            hIdx    = legend.index("HomeTeam")
            aIdx    = legend.index("AwayTeam")
            hfIdx   = legend.index("HF")
            afIdx   = legend.index("AF")
            hyIdx   = legend.index("HY")
            ayIdx   = legend.index("AY")
            hrIdx   = legend.index("HR")
            arIdx   = legend.index("AR")
            col     = 0
            
            # Write the season name in first row
            sheet.write(row, col, rowName + "(Fouls)")
            sheet.write(row + offset, col, rowName + "(Yellow cards)")
            sheet.write(row + 2 * offset, col, rowName + "(Red cards)")
            col += 1
            
            # Process all games of a season
            for line in lines:
                arr = line.split(",");
                home = arr[hIdx].strip()
                away = arr[aIdx].strip()

                # We are only interested in 'teamname'
                if home != teamname and away != teamname:
                  continue;

                if home == teamname:
                  sheet.write(row, col, int(arr[hfIdx].strip()))
                  sheet.write(row + offset, col, int(arr[hyIdx].strip()))
                  sheet.write(row + 2 * offset, col, int(arr[hrIdx].strip()))
                elif away == teamname:
                  sheet.write(row, col, int(arr[afIdx].strip()))
                  sheet.write(row + offset, col, int(arr[ayIdx].strip()))
                  sheet.write(row + 2 * offset, col, int(arr[arIdx].strip()))
                col += 1 # (Row, Col) -> (Season, Game)
        
        
    # Main loop of the program
    def run(self):
        wb          = Workbook() # Workbook where the results will be written
        pointsSheet = wb.add_sheet("Points") # 1 sheet for points scored
        foulsSheet  = wb.add_sheet("Fouls") # 1 sheet for fouls data
        row         = 0
        http        = httplib2.Http()

        status, response = http.request(self.webUrl)
        soup = BeautifulSoup(response, "html.parser")
        for link in soup.find_all("a"):
            if "E0.csv" in link.get("href"):
                # Process current season
                dataUrl = "http://www.football-data.co.uk/" + link.get("href")
                print("processing " + dataUrl)
                curPage = self.get_page(dataUrl) # Read current season's .csv file
                rowName = dataUrl.split("/")[-2]
                rowName = rowName[:2] + "/" + rowName[2:] # 1920 -> 19/20
                self.parse_results(curPage, rowName, "Arsenal", row, pointsSheet)
                self.parse_fouls(curPage, rowName, "Arsenal", row, foulsSheet, 30)
                row += 1

        wb.save("result.xls")
