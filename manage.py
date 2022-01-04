from os import system
from sys import argv

def usage():
    print("""Usage: python manage.py [OPTION]

help              List of available commands
start             Start the price checker application""")

def start():
    system("python price-checker.py")

def main():
    """Main function of the program"""

    list_of_commands = [
        "help",
        "start"
    ]
    
    # Allow only one argument
    if len(argv) > 2:
        exit("Too many arguments. Terminating the program.")
        
    if len(argv) <= 1:
        usage()
        exit()

    # Check for arguments and execute them accordingly
    if argv[1] not in list_of_commands:
        print("No commands were found.")
    else:
        # Find commands based on a dictionary with keys for each command
        switcher = {
            "help": usage,
            "start": start,
        }
        key = argv[1]
        default = ""
        value = switcher.get(key, default)

        # Execute command. Raise error if the command is not in the dictionary
        try:
            value()
        except TypeError:
            print('Missing entry "%s" in the switcher dictionary.' % (key,))

if __name__ == "__main__":
    main()