import os
import os.path

class FileUtils:
    @staticmethod
    def append(file_name, text):
        f = open(file_name, "a")
        f.write(text)
        f.write("\r\n")
        f.close()

    @staticmethod
    def remove_file(file_name):
        os.remove(file_name)

    @staticmethod
    def read_lines(file_name):
        lines_result = []
        f = open(file_name, 'r')
        lines = f.readlines()

        for line in lines:
            line = line.strip()
            lines_result.append(line)
        return lines_result

    @staticmethod
    def file_exists(file_name):
        return os.path.exists(file_name)

    @staticmethod
    def get_file_size(file_name):
        return os.path.getsize(file_name)
