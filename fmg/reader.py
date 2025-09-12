from io import BufferedReader


class FmgReader:
    @staticmethod
    def read_int(file: BufferedReader, int_type: int, offset: int) -> int:
        file.seek(offset)

        match int_type:
            case 8:
                byte = file.read(1)
            case 32:
                byte = file.read(4)

        value = int.from_bytes(byte, byteorder='little', signed=True)
        return value

    @staticmethod
    def read_unicode_string(file: BufferedReader, offset: int) -> str:
        file.seek(offset)
        result = str()

        while True:
            byte = file.read(2)
            char = byte.decode('utf-16-le')

            if char == '\x00':
                break

            result += char

        return result


if __name__ == '__main__':
    pass
