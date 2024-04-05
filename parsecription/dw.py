import csv
with open('CSVgg.csv', newline='') as csvfile:
    # Create a CSV reader object
    csv_reader = csv.reader(csvfile)
    # Iterate over each row in the CSV file
    for row in csv_reader:
        print(row)
