from collections import UserDict
from datetime import datetime, date, timedelta

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter the argument for the command."
        except NameError:
            return "Contact not found."
    return inner

class Field:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)
    

class Phone(Field):
    def __init__(self, value):
        if not value or not value.isdigit() or len(value) != 10:
            raise ValueError("Phone cannot be empty")
        super().__init__(value)

    
class Birthday(Field):
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError("Birthday must be a string in format DD.MM.YYYY")
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)
    

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None


    def add_phone(self, phone):
        phone = Phone(phone)
        if phone not in self.phones:
            self.phones.append(phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def remove_phone(self, phone):
        p = self.find_phone(phone)
        if p.value == phone:
            self.phones.remove(p)
            return True
        return False

    def edit_phone(self, phone, new_p):
        p = self.find_phone(phone)
        if not p:
            raise ValueError("Old phone number not found")
        self.phones.remove(p)
        self.add_phone(new_p)
        return True

        

    

    def __str__(self):
        return (f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)},"
                f" birthday: {self.birthday.value if self.birthday else "Not set"}")


class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
 

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()

        for record in self.data.values():
            if not record.birthday:
                continue
            try:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            except ValueError:
                continue
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_until_birthday = (birthday_this_year - today).days

            if 0 <= days_until_birthday <= days:
                if birthday_this_year.weekday() >= 5:
                    birthday_this_year += timedelta(days=(7 - birthday_this_year.weekday()))
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": birthday_this_year.strftime("%d.%m.%Y")
                })
        return upcoming_birthdays

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    msg = "Contact updated."

    if not record:
        record = Record(name)
        book.add_record(record)
        msg = "Contact added."

    record.add_phone(phone)
    return msg


@input_error
def change_contact(args, book):
    if len(args) != 3:
        return f'Error: You must enter a name, old number and new number.'

    name, phone, new_p = args
    record = book.find(name)
    if not record:
        return f"Contact not found."
    record.edit_phone(phone, new_p)
    return "Contact updated."


@input_error
def show_phones(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    return "; ".join(p.value for p in record.phones)


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    if not record.birthday:
        return "Birthday not set."
    return record.birthday.value


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    lines = [f"{item['name']}: {item['birthday']}" for item in upcoming]
    return "\n".join(lines)




def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args




def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue
        command, args = parse_input(user_input)

        if command in ("close", "exit"):
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            for rec in book.data.values():
                print(rec)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()