import pandas as pd

def updateData():
    print("update data")
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()
def updateDataSentiment():
    print("update data sentiment")
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()
def lihatData():
    print("lihat data")
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()
def visualisasi():
    print("visualisasi")
    anykey=input("Tekan apapun untuk kembali ke menu")
    mainMenu()



def mainMenu():
    print("1. Update data")
    print("2. Update nilai Sentiment")
    print("3. Lihat data")
    print("4. Visualisasi")
    print("5. Keluar")
    selection=int(input("Input anda : "))
    
    try:
        if selection == 1:
            updateData()
        elif selection == 2:
            updateDataSentiment()
        elif selection == 3:
            lihatData()
        elif selection == 4:
            visualisasi()
        elif selection == 5:
            exit
        else:
            print("\nInputlah angka 1 <= 5 ..!\n")
            mainMenu()
    except ValueError:
        print("input anda salah..! Input 1 - 5")
mainMenu()
