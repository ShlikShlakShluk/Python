import csv 

ALL_MONTHS = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]

class ExamException(Exception):
    pass

def posteriore(d2, d1):
    anno_precedente, mese_precedente = map(int, d1.split('-'))
    anno_attuale, mese_attuale = map(int, d2.split('-'))
    if anno_attuale > anno_precedente:
        return True
    elif anno_attuale == anno_precedente and mese_attuale > mese_precedente:
        return True
    else:
        return False

class CSVTimeSeriesFile:
    def __init__(self, name):
        self.name = name

    def get_data(self):
        try:
            with open(self.name, "r") as file:
                
                csv_reader = csv.reader(file, delimiter=',')
                time_series = []
                previous_date = None
                for row in csv_reader:
                    if len(row) < 2: 
                        continue
                    date = row[0].strip()
                    passengers = row[1].strip()
                    
                    try:
                        year, month = date.split('-')
                        yearInt = int(year)
                        monthInt = int(month)
                        passengers = int(passengers)
                        
                    except:
                        continue
                    
                    if previous_date:
                        if not posteriore(date, previous_date):
                            raise ExamException("Timestamp is not ordered or duplicated.")

                    previous_date = date
                    time_series.append([date, passengers])

            return time_series

        except FileNotFoundError:
            raise ExamException('Errore, file non trovato')
        except Exception as e:
            raise ExamException(f'Errore nella lettura del file: {e}')
#Trasformo serie temporale in dizionario annidato
def time_series_as_dict(time_series, start, end):
    dictYears = {}
    for y in range(start, end + 1): 
        dictYears[y] = {}
        for m in ALL_MONTHS:
            dictYears[y][m] = None
    #Popoliamo il dizionario con i valori della serie
    for row in time_series:
        date, passengers = row
        y, m = date.split("-")
        y = int(y)

        if y not in range(start, end + 1):
            continue        
        dictYears[y][m] = int(passengers) 
        
    return dictYears
#controllo se first year o last year sono nel file o no
def allMonthsBad(dict, y):
    monthsValues = dict[y].values()
    # restituisce True se ci sono solo None
    return set(monthsValues) == set([None])
    

def compute_avg_monthly_difference(time_series, first_year, last_year):
    endYear = int(last_year)
    startYear = int(first_year)
    dataDict = time_series_as_dict(time_series, startYear, endYear)
    #Controlla se first year o last year sono nel file o no
    if allMonthsBad(dataDict, startYear) or allMonthsBad(dataDict, endYear):
        
        raise ExamException("startYear or endYear not in the file")
    
    result = []

    for m in ALL_MONTHS:
        goodYears = [y for y in dataDict.keys() if dataDict[y][m] is not None]
        goodYears = sorted(goodYears)

        countOccurrences = len(goodYears)
        #Meno di 2 misurazioni, salto
        if countOccurrences < 2:
            result.append(0.0)
            continue
        
        sum_diff = 0.0

        for i in range(1, len(goodYears)):
            year_current = goodYears[i]
            year_previous = goodYears[i - 1]
            num = dataDict[year_current][m]
            numPrec = dataDict[year_previous][m]
            if num is None or numPrec is None:
                continue
            sum_diff += num - numPrec

        result.append(sum_diff / (countOccurrences - 1))
    
    return result




