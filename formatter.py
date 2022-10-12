import sys
import re
from tabulate import tabulate
from typing import List


class GPSSFileFormatter():
    def __init__(self, file_path: str):
        if self._has_extension(file_path):
            self.file_name = file_path.split('.')[0]
            self.file_path = file_path
        else:
            self.file_name = file_path
            self.file_path = file_path + '.txt'

        self.suffix = 'formatted'
        self.extension = self.file_path.split('.')[-1]

    def _has_extension(self, file_path: str) -> bool:
        """ Checks if file has .gps or .txt extension """
        file_extension = file_path.split('.')

        if len(file_extension) > 1:
            if file_extension[-1] not in ('gps', 'txt'):
                raise Exception('Файл должен быть с расширением gps или txt')
            return True
        # if it's just a file name - return false
        return False

    def format(self):
        """ Format file (remove comments and other shit) """
        if self.file_path.split('.')[-1] == 'txt':
            self._format_txt()
        else:
            self._format_gps()

    def _format_txt(self):
        lines = self.read_txt_file()
        lines = self._format_lines(lines)
        self.write_into_txt_file(lines)

    def _format_gps(self):
        lines = self.read_gps_file()
        lines = self._format_lines(lines)
        self.write_into_gps_file(lines)


    def read_txt_file(self) -> List[str]:
        with open(self.file_path, 'r') as file:
            return file.readlines()

    def read_gps_file(self):
        raise NotImplementedError('[ERROR] Неа, не могу читать эту хуйню. Давай лучше скопируешь в .txt')

    def _format_lines(self, lines: List[str]) -> List[str]:
        for line_index in range(len(lines)):
            # remove comments
            lines[line_index] = lines[line_index].split(';')[0]
            if not lines[line_index].endswith('\n'):
                lines[line_index] += '\n'

        lines = self._remove_extra_lines(lines)

        # TODO: refactor this
        lines = [re.split(r'\s+|\t+', line) for line in lines]

        # remove all spaces after line
        for index, line in enumerate(lines):
            while line:
                if not line[-1]:
                    lines[index].pop()
                else: 
                    break

        max_line_len = len(max(lines))

        for line in lines:
            line_length_delta = max_line_len - len(line)
            if (line_length_delta >= 2 and max_line_len > 2) or (line_length_delta >= 1 and max_line_len <= 2):
                for word in line:
                    if word.strip().startswith('TERMINATE'):
                        line_length_delta -= 1
            for _ in range(line_length_delta):
                line.insert(0, '')

        lines = [x for x in tabulate(lines, rowalign='right').split('\n')]

        # remove first and last lines in tabulate string
        lines.pop(0)
        lines.pop()

        lines = [line + '\n' for line in lines]

        return lines

    def _remove_extra_lines(self, lines: List[str]) -> List[str]:
        indexes_to_pop = []

        if lines[0] == '\n':
            indexes_to_pop.append(0)

        for line_index in range(0, len(lines) - 1):
            if lines[line_index] == lines[line_index + 1] and lines[line_index] == '\n':
                indexes_to_pop.append(line_index)

        for index in indexes_to_pop:
            lines.pop(index)
        
        return lines
    
    def write_into_txt_file(self, lines: List[str]) -> None:
        new_file_name = self.get_new_file_name()

        with open(new_file_name, 'w') as file:
            file.writelines(lines)

    def write_into_gps_file(self, lines: List[str]) -> None:
        raise NotImplementedError('[ERROR] Могу записать только в txt файл. Пока что')

    def get_new_file_name(self) -> str:
        return f'{self.file_name}_{self.suffix}.{self.extension}'

        
def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]    # get drag'n'dropped (or pasted in the prompt) file name
    else:
        file_path = input('Введите название файла/путь к файлу: ')

    formatter = GPSSFileFormatter(file_path)

    formatter.format()

    print(f'Файл был успешно отформатирован и сохранён в {formatter.get_new_file_name()}')


if __name__ == '__main__':
    main()
