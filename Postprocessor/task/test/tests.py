from hstest import *
import random
import hashlib
import os
import string


class Test(StageTest):
    def random_word(self, length):
        letters = string.ascii_lowercase
        capital_letter = random.choice(string.ascii_uppercase)
        return capital_letter + ''.join(random.choice(letters) for i in range(length))

    def random_password(self):
        buffer = string.ascii_lowercase + string.digits
        return ''.join(random.sample(buffer, 8))

    def create_file(self, variant):
        if variant == 'database':
            with open("database.csv", "a") as file:
                file.write('id, nickname, password, consent to mailing')
                for index in range(1, 101):
                    name = random.choice([self.random_word(8), '-'])
                    password = self.random_password()
                    mailing = random.choice(['yes', 'no', '-'])
                    line = f'\n{index}, {name}, {password}, {mailing}'
                    file.write(line)
        if variant == 'hash_database':
            with open("hash_database.csv", "a") as file:
                file.write('id, nickname, password, consent to mailing\n')
        if variant == 'filtered_database':
            with open("filtered_database.csv", "a") as file:
                file.write('id, nickname, password, consent to mailing\n')

    @dynamic_test()
    def test(self):
        random.seed(88)

        if not os.path.isfile('database.csv'):
            self.create_file('database')

        with open('database.csv') as f:
            lines = [line.strip('\n').split(', ') for line in f if len(line) > 1]
            if len(lines) < 101:
                open('database.csv', 'w').close()
                self.create_file('database')
                lines = [line.strip('\n').split(', ') for line in f if len(line) > 1]
            lines.pop(0)

        if not os.path.isfile('hash_database.csv'):
            self.create_file('hash_database')

        if not os.path.isfile('filtered_database.csv'):
            self.create_file('filtered_database')

        main = TestedProgram()
        main.start()

        with open('hash_database.csv') as f:
            hash_lines = [hash_line.split(', ') for hash_line in f if len(hash_line) > 1]
            if not hash_lines or hash_lines[0] != ['id', 'nickname', 'password', 'consent to mailing\n']:
                return CheckResult.wrong("It looks like your file is missing the first line 'id, nickname, password, " 
                                         "consent to mailing'. It should be in the first place, "
                                         " as indicated in the screenshot in the task.")
            if len(hash_lines) < 101:
                return CheckResult.wrong("It looks like your hash_database.csv file has fewer lines "
                                         "than your original database.csv file. You may have lost some lines!")
            if len(hash_lines) > 101:
                return CheckResult.wrong("It seems your hash_database.csv file contains more rows than expected!"
                                         " You may have duplicated the data!")

        with open('filtered_database.csv') as f:
            lines = [line.split(', ') for line in f if len(line) > 1]
            if len(lines) < 30:
                return CheckResult.wrong(f'It looks like you deleted some data because the expected number' +
                                         f' of non-blank lines is 30, but there are {len(lines)}'
                                         f' non-blank lines in your file')

            if len(lines) > 30:
                return CheckResult.wrong(f'It looks like you added some extra data because the expected number' +
                                         f' of non-blank lines is 30, but there are {len(lines)}'
                                         f' non-blank lines in your file')

            lines.pop(0)

        with open('./test/tests_filtered_database.csv') as f:
            tests_lines = [line.split(', ') for line in f if len(line) > 1]
            tests_lines.pop(0)

        random_line = random.choice(lines)
        random_id = int(random_line[0])

        if random_line != tests_lines[random_id - 1]:
            return CheckResult.wrong(f'Your user information: {random_line},'
                                     f' although the following line was expected: {tests_lines[random_id - 1]}')

        return CheckResult.correct()


if __name__ == '__main__':
    Test().run_tests()
