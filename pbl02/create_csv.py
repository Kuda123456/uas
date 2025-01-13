import csv

# Data yang akan dimasukkan ke file CSV
data = [
    ['make', 'model', 'year', 'price'],  # Header
    ['Toyota', 'Corolla', 2020, 20000],
    ['Honda', 'Civic', 2019, 18000],
    ['Ford', 'Focus', 2021, 22000]
]

# Membuat file CSV
with open('cars.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    # Menulis data ke dalam CSV
    writer.writerows(data)

print("File CSV telah dibuat!")
