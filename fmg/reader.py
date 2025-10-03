from io import BufferedReader
import struct


class FmgReader:
    @staticmethod
    def read_int(file: BufferedReader, int_type: int, offset: int) -> int:
        file.seek(offset)

        match int_type:
            case 8:
                size = 1
                format_char = 'b'
            case 32:
                size = 4
                format_char = 'i'

        data = file.read(size)
        return struct.unpack('<' + format_char, data)[0]

    @staticmethod
    def read_unicode_string(file: BufferedReader, offset: int) -> str:
        file.seek(offset)

        max_bytes = 4096
        data = file.read(max_bytes)

        for i in range(0, len(data) - 1, 2):
            if data[i] == 0 and data[i + 1] == 0:
                data = data[:i]
                break

        return data.decode('utf-16-le') if data else ''


if __name__ == '__main__':
    pass
