import csv
import os

import pandas as pd


class DramMemory_inMem:
    def __init__(self, size, outpath="output/"):
        self.DataStore = [0x0] * size
        # self.size = size
        # self.rows = 16384
        # self.words_per_row = 64
        # self.bytes_in_file = self.rows*self.words_per_row*4 # rows * bytes_per_row
        # num_files, leftover = divmod(size, self.bytes_in_file)
        # if leftover != 0:
        #    num_files = num_files+1
        self.read_bytes = 0
        self.write_bytes = 0
        # print("Num Files: %d" % num_files)
        # for num in range(num_files):
        #    start_addr = num*self.bytes_in_file
        #    end_addr = start_addr + self.bytes_in_file
        #    filename = outpath + "memdata_" + str(start_addr) + "_" + str(end_addr) + ".csv"
        #    self.memfile_list.append(filename)
        #    with open(filename, "w+") as f:
        #        addr=start_addr
        #        f_csv = csv.writer(f)
        #        header_row = [x for x in range(self.words_per_row)]
        #        header_row = ['addr'] + header_row
        #        f_csv.writerow(header_row)
        #        for j in range(self.rows):
        #            row = [0 for x in range(self.words_per_row)]
        #            #print("addr: %d" % addr+j*128)
        #            row = [str(j), str(hex(addr))] + row
        #            f_csv.writerow(row)
        #            addr=addr+self.words_per_row*4
        #            if addr>self.size:
        #                break
        #    f.close()

    def read_word(self, byte_addr):
        wd_data = self.DataStore[byte_addr >> 2]
        wd_next_data = self.DataStore[(byte_addr >> 2) + 1]
        self.read_bytes += 4
        if byte_addr % 4 == 0:
            return wd_data
        if byte_addr % 4 == 1:
            return (wd_data & 0x00FFFFFF) << 8 | (wd_next_data & 0xFF000000) >> 24
        if byte_addr % 4 == 2:
            return (wd_data & 0x0000FFFF) << 16 | (wd_next_data & 0xFFFF0000) >> 16
        else:
            return (wd_data & 0x000000FF) << 24 | (wd_next_data & 0xFFFFFF00) >> 8

    def read_dram_block(self, byte_addr, size):
        num_words, sub_word = divmod(size, 4)
        # return_data = [0 for i in range(num_words)]
        return_data = []
        self.read_bytes += 4 * num_words
        for i in range(num_words):
            if byte_addr % 4 == 0:
                return_data.append(self.DataStore[(byte_addr >> 2) + i])
            else:
                wd_data = self.DataStore[(byte_addr >> 2) + i]
                wd_next_data = self.DataStore[(byte_addr >> 2) + i + 1]
                # print("byte_addr>>2+i:%d" %((byte_addr>>2)+i))
                # print("byte_addr>>2+i+1:%d" %((byte_addr>>2)+i+1))
                # print("DataStore[%d]:%d" %((byte_addr>>2)+i, wd_data))
                # print("DataStore[%d]:%d" %((byte_addr>>2)+i+1,wd_next_data))
                if byte_addr % 4 == 1:
                    return_data.append(((wd_data & 0x00FFFFFF) << 8) | ((wd_next_data & 0xFF000000) >> 24))
                elif byte_addr % 4 == 2:
                    return_data.append(((wd_data & 0x0000FFFF) << 16) | ((wd_next_data & 0xFFFF0000) >> 16))
                else:
                    return_data.append(((wd_data & 0x000000FF) << 24) | ((wd_next_data & 0xFFFFFF00) >> 8))
            print(return_data)
        return return_data

    def write_word(self, byte_addr, wd_data):
        old_wd_data = self.DataStore[byte_addr >> 2]
        next_wd_data = self.DataStore[(byte_addr >> 2) + 1]
        self.write_bytes += 4
        if byte_addr % 4 == 0:
            self.DataStore[byte_addr >> 2] = wd_data
        elif byte_addr % 4 == 1:
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFF000000 | (wd_data & 0xFFFFFF00) >> 8
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x00FFFFFF | (wd_data & 0x000000FF) << 24
        elif byte_addr % 4 == 2:
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFFFF0000 | (wd_data & 0xFFFF0000) >> 16
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x0000FFFF | (wd_data & 0x0000FFFF) << 16
        else:
            self.DataStore[byte_addr >> 2] = old_wd_data & 0xFFFFFF00 | (wd_data & 0xFF000000) >> 24
            self.DataStore[(byte_addr >> 2) + 1] = next_wd_data & 0x000000FF | (wd_data & 0x00FFFFFF) << 8

    def write_dram_block(self, byte_addr, data):
        num_words = len(data)
        self.write_bytes += 4 * num_words
        #        return_data = [0 for i in range(num_words)]
        for i in range(num_words):
            # print("Writing data[%d]:%d" %(i, data[i]))
            # print("byte_addr_mod_4:%d" %(byte_addr%4))
            # print("byte_addr>>2+i:%d" %((byte_addr>>2)+i))
            # print("byte_addr>>2+i+1:%d" %((byte_addr>>2)+i+1))
            if byte_addr % 4 == 0:
                self.DataStore[byte_addr >> 2 + i] = data[i]
            else:
                old_wd_data = self.DataStore[(byte_addr >> 2) + i]
                next_wd_data = self.DataStore[(byte_addr >> 2) + 1 + i]
                print("old_wd_data:%d" % (old_wd_data))
                print("next_wd_data:%d" % (next_wd_data))
                if byte_addr % 4 == 1:
                    self.DataStore[(byte_addr >> 2) + i] = old_wd_data & 0xFF000000 | (data[i] & 0xFFFFFF00) >> 8
                    self.DataStore[(byte_addr >> 2) + 1 + i] = next_wd_data & 0x00FFFFFF | (data[i] & 0x000000FF) << 24
                elif byte_addr % 4 == 2:
                    self.DataStore[(byte_addr >> 2) + i] = old_wd_data & 0xFFFF0000 | (data[i] & 0xFFFF0000) >> 16
                    self.DataStore[(byte_addr >> 2) + 1 + i] = next_wd_data & 0x0000FFFF | (data[i] & 0x0000FFFF) << 16
                else:
                    self.DataStore[(byte_addr >> 2) + i] = old_wd_data & 0xFFFFFF00 | (data[i] & 0xFF000000) >> 24
                    self.DataStore[(byte_addr >> 2) + 1 + i] = next_wd_data & 0x000000FF | (data[i] & 0x00FFFFFF) << 8
                print("DataStore[%d]:%d" % ((byte_addr >> 2) + i, self.DataStore[(byte_addr >> 2) + i]))
                print("DataStore[%d]:%d" % ((byte_addr >> 2) + i + 1, self.DataStore[(byte_addr >> 2) + 1 + i]))

    def printstats(self, filename):
        with open(filename, "a+") as f:
            f.write("dram_write_bytes:%d\n" % self.write_bytes)
            f.write("dram_read_bytes:%d\n" % self.read_bytes)
        f.close()


class DramMemory:
    def __init__(self, size, outpath="output/"):
        # self.Data = [0x0] * size
        self.memfile_list = []
        self.size = size
        self.rows = 16384
        self.words_per_row = 64
        self.bytes_in_file = self.rows * self.words_per_row * 4  # rows * bytes_per_row
        num_files, leftover = divmod(size, self.bytes_in_file)
        if leftover != 0:
            num_files = num_files + 1
        self.read_bytes = 0
        self.write_bytes = 0
        print("Num Files: %d" % num_files)
        for num in range(num_files):
            start_addr = num * self.bytes_in_file
            end_addr = start_addr + self.bytes_in_file
            filename = outpath + "memdata_" + str(start_addr) + "_" + str(end_addr) + ".csv"
            self.memfile_list.append(filename)
            with open(filename, "w+") as f:
                addr = start_addr
                f_csv = csv.writer(f)
                header_row = [x for x in range(self.words_per_row)]
                header_row = ["addr"] + header_row
                f_csv.writerow(header_row)
                for j in range(self.rows):
                    row = [0 for x in range(self.words_per_row)]
                    # print("addr: %d" % addr+j*128)
                    row = [str(j), str(hex(addr))] + row
                    f_csv.writerow(row)
                    addr = addr + self.words_per_row * 4
                    if addr > self.size:
                        break
            f.close()

    def setup(self, filename):
        return 0

    def read_word(self, byte_addr):
        file_num, file_mod = divmod(byte_addr, self.bytes_in_file)
        rownum, colbyte = divmod(file_mod, self.words_per_row * 4)
        colnum = colbyte >> 2
        last_byte_in_file = 0
        last_byte_in_row = 0
        last_file_in_range = 0
        memfile = self.memfile_list[file_num]
        df = pd.read_csv(memfile)
        if (file_num + 1) != len(self.memfile_list):
            next_memfile = self.memfile_list[file_num + 1]
            df_next = pd.read_csv(next_memfile)
        else:
            last_file_in_range = 0
        if (file_mod + 4) >= self.bytes_in_file:
            last_byte_in_file = 1
        if (colnum + 1) % self.words_per_row == 0:
            last_byte_in_row = 1
        wd_data = df.at[rownum, str(colnum)]
        if last_byte_in_file and not last_file_in_range:
            wd_next_data = df_next.at[0, str("0")]
        elif last_byte_in_file and last_file_in_range:
            _wd_next_data = 0
        elif last_byte_in_row:
            wd_next_data = df.at[rownum + 1, str("0")]
        else:
            wd_next_data = df.at[rownum, str(colnum + 1)]
        if byte_addr % 4 == 0:
            self.read_bytes += 4
            return wd_data
        if byte_addr % 4 == 1:
            self.read_bytes += 4
            return (wd_data & 0x00FFFFFF) << 8 | (wd_next_data & 0xFF000000) >> 24
        if byte_addr % 4 == 2:
            self.read_bytes += 4
            return (wd_data & 0x0000FFFF) << 16 | (wd_next_data & 0xFFFF0000) >> 16
        else:
            self.read_bytes += 4
            return (wd_data & 0x000000FF) << 24 | (wd_next_data & 0xFFFFFF00) >> 8

    def write_word(self, byte_addr, wd_data):
        file_num, file_mod = divmod(byte_addr, self.bytes_in_file)
        rownum, colbyte = divmod(file_mod, self.words_per_row * 4)
        colnum = colbyte >> 2
        last_byte_in_file = 0
        last_byte_in_row = 0
        last_file_in_range = 0
        memfile = self.memfile_list[file_num]
        df = pd.read_csv(memfile, index_col=0)
        if (file_num + 1) != len(self.memfile_list):
            next_memfile = self.memfile_list[file_num + 1]
            df_next = pd.read_csv(next_memfile, index_col=0)
        else:
            last_file_in_range = 1
        if (file_mod + 4) >= self.bytes_in_file:
            last_byte_in_file = 1
        if (colnum + 1) % self.words_per_row == 0:
            last_byte_in_row = 1
        # print(df.loc[rownum, str(colbyte>>2)])
        old_wd_data = df.at[rownum, str(colnum)]
        if last_byte_in_file and not last_file_in_range:
            next_wd_data = df_next.at[0, str("0")]
        elif last_byte_in_file and last_file_in_range:
            next_wd_data = 0
        elif last_byte_in_row:
            next_wd_data = df.at[rownum + 1, str("0")]
        else:
            next_wd_data = df.at[rownum, str(colnum + 1)]
        # df.loc[rownum, str(colnum*4)] = wd_data
        # old_wd_data = self.Data[byte_addr>>2]
        # next_wd_data = self.Data[(byte_addr>>2)+1]
        if byte_addr % 4 == 0:
            self.write_bytes += 4
            df.loc[rownum, str(colnum)] = wd_data
        elif byte_addr % 4 == 1:
            self.write_bytes += 4
            df.loc[rownum, str(colnum)] = old_wd_data & 0xFF000000 | (wd_data & 0xFFFFFF00) >> 8
            if last_byte_in_row:
                df.loc[rownum + 1, str("0")] = next_wd_data & 0x00FFFFFF | (wd_data & 0x000000FF) << 24
            elif last_byte_in_file and not last_file_in_range:
                df_next.loc[0, "0"] = next_wd_data & 0x00FFFFFF | (wd_data & 0x000000FF) << 24
            else:
                df.loc[rownum, str(colnum + 1)] = next_wd_data & 0x00FFFFFF | (wd_data & 0x000000FF) << 24

        elif byte_addr % 4 == 2:
            self.write_bytes += 4
            df.loc[rownum, str(colnum)] = old_wd_data & 0xFFFF0000 | (wd_data & 0xFFFF0000) >> 16
            if last_byte_in_row:
                df.loc[rownum + 1, str("0")] = next_wd_data & 0x0000FFFF | (wd_data & 0x0000FFFF) << 16
            elif last_byte_in_file and not last_file_in_range:
                df_next.loc[rownum, str(colnum + 1)] = next_wd_data & 0x0000FFFF | (wd_data & 0x0000FFFF) << 16
            else:
                df.loc[rownum, str(colnum + 1)] = next_wd_data & 0x0000FFFF | (wd_data & 0x0000FFFF) << 16
        else:
            self.write_bytes += 4
            df.loc[rownum, str(colnum)] = old_wd_data & 0xFFFFFF00 | (wd_data & 0xFF000000) >> 24
            if last_byte_in_row:
                df.loc[rownum + 1, str("0")] = next_wd_data & 0x000000FF | (wd_data & 0x00FFFFFF) << 8
            elif last_byte_in_file and not last_file_in_range:
                df.loc[0, str("0")] = next_wd_data & 0x000000FF | (wd_data & 0x00FFFFFF) << 8
            else:
                df.loc[rownum, str(colnum + 1)] = next_wd_data & 0x000000FF | (wd_data & 0x00FFFFFF) << 8
        df.to_csv(memfile, index=True)
        if last_byte_in_file and not last_file_in_range:
            df_next.to_csv(next_memfile, index=True)

    def write_burst(self, byte_addr, data):
        burst_len = len(data)

    def dump_memory(self, filename):
        with open(filename, "w") as f:
            for i in range(self.size):
                line = str()


if __name__ == "__main__":
    test_memory = DramMemory_inMem(16770000)
    test_memory.write_word(4122, 4)
    print(test_memory.read_word(4122))
    data = [4, 16, 32, 64]
    test_memory.write_dram_block(4122, data)
    read_data = test_memory.read_dram_block(4122, 16)
    for data_rd in read_data:
        print(data_rd)
