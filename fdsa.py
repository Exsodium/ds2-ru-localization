import struct
import io


class FmgEdit:
    bigendian = False
    fs = None

    def btn_open_click(self, file_path: str):
        with open(file_path, 'rb') as self.fs:
            self.bigendian = self.r_int8(9) == -1

            num_entries = self.r_int32(0x0C)
            start_offset = self.r_int32(0x14)

            for i in range(num_entries):
                start_index = self.r_int32(0x1C + i * 0x0C)
                start_id = self.r_int32(0x1C + i * 0x0C + 4)
                end_id = self.r_int32(0x1C + i * 0x0C + 8)

                for j in range(start_id, end_id + 1):
                    txt_offset = self.r_int32(
                        start_offset + (start_index + j - start_id) * 4)
                    txt = ""
                    if txt_offset > 0:
                        txt = self.r_uni_string(txt_offset)
                        txt = txt.replace('\n', '/n/')
                    # Предполагаем, что dgvTextEntries - это список или DataFrame
                    # dgvTextEntries.append((j, txt))
                    print(f"ID: {j}, Text: {txt}")

    def r_int8(self, loc: int) -> int:
        if loc is not None:
            self.fs.seek(loc)
        byte = self.fs.read(1)
        value = int.from_bytes(
            byte, byteorder='big' if self.bigendian else 'little', signed=True)
        return value

    def r_int32(self, loc: int) -> int:
        self.fs.seek(loc)
        byte = self.fs.read(4)
        if self.bigendian:
            byte = byte[::-1]
        return int.from_bytes(byte, byteorder='little', signed=True)

    def r_uni_string(self, loc: int) -> str:
        self.fs.seek(loc)
        result = []
        while True:
            byte = self.fs.read(2)
            if not byte:
                break
            if self.bigendian:
                byte = byte[::-1]
            char = byte.decode('utf-16-le')
            if char == '\x00':
                break
            result.append(char)
        return ''.join(result)


fmg = FmgEdit()
fmg.btn_open_click('bofire.fmg')
