import pickle

from datetime import datetime, timedelta
from collections import UserDict


# Базовий клас для полів запису.
class Field:
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return str(self.value)


# Клас для зберігання імені контакту
class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError('Name cannot be empty.')
        super().__init__(value)


# Клас для зберігання номера телефону.
class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError('Phone is required')
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError('Birthday must be in the format DD.MM.YYYY.')


# Клас для зберігання інформації про контакт
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None


    def add_phone(self, phone):
        self.phones.append(Phone(phone))


    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError('Phone not found')


    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            phone_obj.value = new_phone
        else:
            raise ValueError('Old phone not found')


    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None


    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)


    def __str__(self):
        return f"Contact name: {self.name.value}, phone: {'; '.join(p.value for p in self.phones)}{f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""}"


# Клас для зберігання та управління записами.
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record


    def find(self, name):
        return self.data.get(name)


    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError('Contact not found')
        
    
    def get_upcoming_birthdays(self, days=7):
        upcoming_birthday = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                days_until_birthday = (birthday_this_year - today).days
                if 0 <= days_until_birthday <= days:
                    if birthday_this_year.weekday() >= 5:
                        birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday))
                    upcoming_birthday.append({
                        "name": record.name.value,
                        "birthday": birthday_this_year.strftime("%d.%m.%Y")
                    })
        return upcoming_birthday


    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
    

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter the argument for the command."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return inner


def parse_input(user_input):
    """Розбирає введену команду та її аргументи."""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook):
    """Додає новий контакт."""
    name, phone, *_ = args
    record = book.find(name)
    message =  "Contact update."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    save_data(book)
    return message


@input_error
def change_contact(args, book: AddressBook):
    """Змінює номер телефону для існуючого контакту."""
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        save_data(book)
        return "Contact update."
    return "Contact not found."


@input_error
def show_phone(args, book: AddressBook):
    """Показує номер телефону для заданого контакту."""
    name = args[0]
    record = book.find(name)
    if record:
        return f"The phone number for {name} is {", ".join([p.value for p in record.phones])}."
    return "Contact not found."


@input_error
def show_all(book: AddressBook):
    """Виводить всі збережені контакти та їхні номери."""
    if not book.data:
        return "No contacts saved."
    result = "\n".join([f"{record.name.value}: {", ".join([p.value for p in record.phones])}" for record in book.values()])
    return result


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record is None:
        return "Contact not found"
    record.add_birthday(birthday)
    save_data(book)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
       return "Contact not found."
    return f"{name}'s birthday is {record.birthday.value.strftime('%d.%m/%Y')}."


@input_error
def birthday(args, book):
    return book.get_upcoming_birthdays()


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthday(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()