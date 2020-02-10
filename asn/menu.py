import asn


def mainMenu():
    def printMainMenu():
        print(30 * "-", "ASN-CALC", 30 * "-")
        print("1. Generate candidates CSV ")
        print("2. Generate citations count CSV ")
        print("3. Calculate indexes and gap between calculated and real data")
        print("4. Analize results and make graphs")
        print("5. Exit")
        print(70 * "-")

    loop = True
    int_choice = -1

    while loop:
        printMainMenu()
        choice = input("Enter your choice (int): ")
        if choice == '1':
            int_choice = 1
            loop = False
        elif choice == '2':
            int_choice = 2
            loop = False
        elif choice == '3':
            int_choice = 3
            loop = False
        elif choice == '4':
            int_choice = 4
            loop = False
        elif choice == '5':
            int_choice = -1
            print("Exiting..")
            loop = False
        else:
            input("Wrong menu selection. Enter any key to try again.")
    return int_choice


def typeMenu():
    def printTypeMenu():
        print("Type of analysis on multiple subjects")
        print("1. Diversificate results based on subject ")
        print("2. Join all results ")
        print(37 * "-")

    loop = True
    int_choice = -1

    while loop:
        printTypeMenu()
        choice = input("Enter your choice (int): ")
        if choice == '1':
            int_choice = 1
            loop = False
        elif choice == '2':
            int_choice = 2
            loop = False
        else:
            input("Wrong menu selection. Enter any key to try again.")
    return int_choice
