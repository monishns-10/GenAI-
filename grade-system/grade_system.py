print("Enter your mark to determine your grade.")

mark = input("Enter your mark (0-100): ")

try:
    mark = int(mark)

    if mark < 0 or mark > 100:
        print("Error: Mark must be between 0 and 100.")

    elif mark >= 90:
        print("Mark:", mark, "-> Grade: A")

    elif mark >= 80:
        print("Mark:", mark, "-> Grade: B")

    elif mark >= 70:
        print("Mark:", mark, "-> Grade: C")

    elif mark >= 60:
        print("Mark:", mark, "-> Grade: D")

    else:
        print("Mark:", mark, "-> Grade: E")

except ValueError:
    print("Error: Please enter a valid number.")