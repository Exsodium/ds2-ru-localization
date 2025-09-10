from io import BufferedReader


class FmgReader:
    is_bigendian = False
    file: BufferedReader = None

    def read_fmg_file(self, file_path: str) -> None:
        with open(file_path, 'rb') as self.file:
            self.bigendian = self.read_int8(9) == -1

            num_entries = self.read_int32(0x0C)
            start_offset = self.read_int32(0x14)

            for i in range(num_entries):
                start_index = self.read_int32(0x1C + i * 0x0C)
                start_id = self.read_int32(0x1C + i * 0x0C + 4)
                end_id = self.read_int32(0x1C + i * 0x0C + 8)

                for j in range(start_id, end_id + 1):
                    txt_offset = self.read_int32(
                        start_offset + (start_index + j - start_id) * 4)
                    txt = ""

                    if txt_offset > 0:
                        txt = self.read_unicode_string(txt_offset)
                        txt = txt.replace('\n', '/n/')

                    print(f"ID: {j}, Text: {txt}")

    def read_int8(self, loc: int) -> int:
        self.file.seek(loc)
        byte = self.file.read(1)
        byteorder = 'big' if self.is_bigendian else 'little'
        value = int.from_bytes(byte, byteorder, signed=True)

        return value

    def read_int32(self, loc: int) -> int:
        self.file.seek(loc)
        byte = self.file.read(4)

        if self.is_bigendian:
            byte = byte[::-1]

        return int.from_bytes(byte, byteorder='little', signed=True)

    def read_unicode_string(self, loc: int) -> str:
        self.file.seek(loc)
        result = []

        while True:
            byte = self.file.read(2)

            if self.is_bigendian:
                byte = byte[::-1]

            char = byte.decode('utf-16-le')

            if char == '\x00':
                break

            result.append(char)

        return ''.join(result)


reader = FmgReader()
reader.read_fmg_file('bofire.fmg')
