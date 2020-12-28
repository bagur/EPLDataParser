from EplDataParser import Parser

def main():
    curParser = Parser('http://www.football-data.co.uk/englandm.php')
    curParser.run()
    
if __name__ == '__main__':
    main()
