import asn


def menu():
    def print_menu():
        print(30 * "-", "ASN-CALC", 30 * "-")
        print("1. Generate candidates CSV ")
        print("2. Generate citations count CSV ")
        print("3. Calculate indexes")
        print("4. Exit")
        print(73 * "-")

    loop = True
    int_choice = -1

    while loop:
        print_menu()
        choice = input("Enter your choice: ")
        path1 = ''
        path2 = ''
        if choice == '1':
            while len(path1) == 0:
                path1 = input("Enter input candidate's tsv file path: ")
            int_choice = 1
            loop = False
        elif choice == '2':
            while len(path1) == 0:
                path1 = input("Enter input COCI data csv file path: ")
            int_choice = 2
            loop = False
        elif choice == '3':
            while len(path1) == 0:
                path1 = input("Enter CANDIDATES_OUT.csv file path: ")
            while len(path2) == 0:
                path2 = input("Enter CITATIONS_OUT.csv file path: ")
            int_choice = 3
            loop = False
        elif choice == '4':
            int_choice = -1
            print("Exiting..")
            loop = False
        else:
            input("Wrong menu selection. Enter any key to try again.")
    return int_choice, path1, path2
