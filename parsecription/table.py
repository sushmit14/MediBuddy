import tabula
path = 'C:/Users/Aryan/Desktop/NaturalQL/Parsecription/report1.pdf'
filename = 'CSVgg.csv'
dfs = tabula.read_pdf(path, pages='all', stream=True)
f = open(filename, 'a')
for df in dfs:
    df.to_csv(f, index=False)
    f.write("\n")
f.close()
