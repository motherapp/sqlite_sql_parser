#The MIT License (MIT)
#
#Copyright (c) 2015 Motherapp Limited
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.


#
#
#
#author: walty@motherapp.com
#description: parse the sql generated from sqlite3, so it could be imported to mysql
#
#reference: http://stackoverflow.com/questions/1067060/translating-perl-to-python
#reference: http://stackoverflow.com/questions/18671/quick-easy-way-to-migrate-sqlite3-to-mysql
#
#

import sys
import re
import datetime

class SQLParser():
    def __init__(self, input_file, output_file):
        self.buffer_string = ""
        self.fin = open(input_file)
        self.fw = open(output_file, "w")

        self.previous_string_quote = ""
        self.buffer_string = ""

        self.literal_string = ""

        self.current_char = ""
        self.prev_char = ""
        self.next_char = ""

        self.current_quote = ""
        self.current_line = ""


        return


    def flush_buffer(self, skip_last_char=False, write_to_file=False):
        if skip_last_char:
            final_buffer = self.buffer_string[:-1]
            self.buffer_string = self.buffer_string[-1] #clean all except last char
        else:
            final_buffer = self.buffer_string
            self.buffer_string = "" #clean all
        

        if self.is_in_quote():
            final_buffer = self.process_literal(final_buffer)  #do misc final processing
        else:
            final_buffer = self.process_non_literal(final_buffer)

        self.current_line += final_buffer

        if(write_to_file):
            final_line = self.process_line(self.current_line)
            self.fw.write(final_line)
            self.current_line = ""

        return

    def add_buffer(self, c):
        self.buffer_string += c



    def read_next_char(self):
        self.prev_char = self.current_char
        self.current_char = self.next_char
        self.next_char = self.fin.read(1)

        if self.current_char:
            self.add_buffer(self.current_char)
        elif self.next_char:#for the first char of the file
            self.read_next_char()

        return self.current_char

    def set_current_quote(self, c):
        self.current_quote = c

    def clean_current_quote(self):
        self.current_quote = ""


    def is_in_quote(self):
        return self.current_quote != ""

    def process_literal(self, value):   #process literal strings
        if value == 't':
            return 1

        if value == 'f':
            return 0

        if self.current_line.endswith("INSERT INTO "):
            return value.strip("\"")    #mysql has no quote for insert into table name

            
        value = value.replace("\\", "\\\\")

        #print "@75: processing literal", value
        return value

    def process_non_literal(self, value):   #process non literal strings
        #print "@79: processing non-literal", value

        value = value.replace("AUTOINCREMENT", "AUTO_INCREMENT")

        #WARNING: NEED TO CUSTOMIZE THE FOLLOWINGS
        value = value.replace(" text,\n", " varchar(255),\n")
        value = value.replace(" text\n", " varchar(255)\n")
        value = value.replace(" integer", " bigint")

        return value

    def process_line(self, value):  #line based processing
        if value.startswith("BEGIN TRANSACTION") or value.startswith("COMMIT") or \
                value.startswith("sqlite_sequence") or value.startswith("CREATE UNIQUE INDEX") or \
                value.startswith("PRAGMA"):
            return ""

        #print "@138", value

        if value.startswith("CREATE TABLE"):
            m = re.search('CREATE TABLE ([a-z_]+)', value)

            if m:
              name, = m.groups()
              line = '''
DROP TABLE IF EXISTS %(name)s;
CREATE TABLE IF NOT EXISTS %(name)s (
'''
              value = line % dict(name=name)


        return value


    def start(self):
        line_number = 1;
        start_time = datetime.datetime.now()



        while True:
            c = self.read_next_char()

            if not c:
                print "End of file"
                break


            if (c == "'" or c == "\""):
                #if self.prev_char == "\\" and self.next_char != c: #it's just an escaped single quote
                #    continue

                if not self.is_in_quote():
                    self.flush_buffer(skip_last_char = True)
                    self.set_current_quote(c)

                elif self.current_quote == c:    #end of string
                    if self.next_char == c: #double single quote, or double double quote
                        self.read_next_char()   #discard the paired one
                        continue
                    else:
                        self.flush_buffer()
                        self.clean_current_quote()


            if (c == "\n" or c == "\r"):
                #flush teh buffer
                line_number += 1

                if line_number % 10000 == 0:
                    print "@51 processing line: ", line_number, "elpased: ", datetime.datetime.now() - start_time, "seconds"

                if not self.is_in_quote():
                    self.flush_buffer(write_to_file = True)
                    
                    #print "@119, current line", self.current_line


        self.flush_buffer(write_to_file = True)

        return

def main():
    if __name__ == "__main__":
        if len(sys.argv) != 3:
            print "Usage: python " + sys.argv[0] + " input_file output_file\n"
            return -1

        input_file = sys.argv[1]
        output_file = sys.argv[2]

        parser = SQLParser(input_file, output_file)

        parser.start()

        print "Done."

main()
