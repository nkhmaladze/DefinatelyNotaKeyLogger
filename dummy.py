import datetime

logfile = "time.txt"

now = datetime.datetime.now()

try:
    with open(logfile, 'w') as file:
        file.write(str(now))
        file.write("\nThe iframe worked!")
except:
    print("Uh oh! Something went wrong.")

print("The iframe worked!")