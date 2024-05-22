import re


class FindContent:
    @staticmethod
    def find_comp_arch_content(pdf_reader, start_page, end_page):
        result = {}
        end_page = min(end_page, len(pdf_reader.pages))
        number = None
        is_content_started = False

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                if "APPENDIX" in line[:9]:
                    break
                if not is_content_started:
                    if "CHAPTER" in line:
                        is_content_started = True
                        number = 1
                        match = re.findall(r"CHAPTER \d\s+", line)
                        chapter_name = line.split(match[0])[1]
                        result[number] = chapter_name.strip().rstrip().lower()
                else:
                    if "CHAPTER" in line:
                        number += 1
                        match = re.findall(r"CHAPTER \d\s+", line)
                        chapter_name = line.split(match[0])[1]
                        result[number] = chapter_name.strip().rstrip().lower()

                    else:
                        line = line.replace("-", "").replace(",",
                                                             "").replace(":",
                                                                         "").replace(";",
                                                                                     "").replace("/",
                                                                                                 "").replace("&", " ")
                        pattern = re.compile(r"\d[.]\d\s+([a-z\s]+)", re.IGNORECASE)
                        match = pattern.findall(line)
                        if len(match) != 0:
                            result[number] += ", " + match[0].rstrip().strip().lower()

        return result

    @staticmethod
    def find_data_intensive_content(pdf_reader, start_page, end_page):
        result = []
        output = {}
        end_page = min(end_page, len(pdf_reader.pages))
        number = None
        number_two = None

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                line = line.replace(".", " ")
                matches = re.findall(r"\s\s\s+", line)
                if len(matches) != 0 and line.split(matches[0])[1].isnumeric():
                    tmp = line.split(matches[0])
                    matched_numbers = re.findall(r"\d+\s", tmp[0])
                    if len(matched_numbers) != 0:
                        number = int(matched_numbers[0].rstrip())
                        number_two = 0
                        line_split = (
                            f"{number}.{number_two}", tmp[0].replace(matched_numbers[0], "").lower(), tmp[1])
                    else:
                        number_two += 1
                        line_split = (f"{number}.{number_two}", tmp[0].lower(), tmp[1])
                    result.append(line_split)
        for i in result:
            unit = i[0].split(".")[0]
            if unit not in output.keys():
                output[unit] = i[1]
            else:
                output[unit] += ", " + i[1]
        return output

    @staticmethod
    def find_ethics_1_content(pdf_reader, start_page, end_page):
        result = {}
        end_page = min(end_page, len(pdf_reader.pages))
        number = None
        is_content_started = False

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                if "Glossary" in line[:9]:
                    break
                if not is_content_started:
                    if "Chapter" in line[:9]:
                        is_content_started = True
                        number = 1
                        match = re.findall(r"Chapter \d+\s+", line)
                        chapter_name = line.split(match[0])[1]
                        result[number] = chapter_name.strip().rstrip().lower()
                else:
                    if "Chapter" in line[:9]:
                        number += 1
                        match = re.findall(r"Chapter \d+\s+", line)
                        chapter_name = line.split(match[0])[1]
                        result[number] = chapter_name.strip().rstrip().lower()

                    else:
                        line = line.replace("-", "").replace(",",
                                                             "").replace(":",
                                                                         "").replace(";",
                                                                                     "").replace("/",
                                                                                                 "").replace("&", " ")
                        match = re.findall(r"\s+\d+", line)

                        if len(match) != 0:
                            result[number] += ", " + line.split(match[0])[0].rstrip().strip().lower()

        return result

    @staticmethod
    def find_ethics_2_content(pdf_reader, start_page, end_page):
        result = {}
        end_page = min(end_page, len(pdf_reader.pages))

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                line = (line.replace("-", " ")
                        .replace(",", "")
                        .replace(":", "")
                        .replace(";", "")
                        .replace("/", " ")
                        .replace("&", " ")
                        .replace('"', "")
                        .replace("'", "")
                        .replace("(", "")
                        .replace(")", ""))
                match = re.findall(r"(\d+)[.]*\d*[.]*\d*\s+[a-zA-Z]*", line)
                line_mod = line.replace(".", "").replace("’", " ").replace("?", "").replace("“", "").replace("”", "")
                match_2 = re.findall(r"\d+[.]*\d*[.]*\d*([a-zA-Z|\s]+)\d+", line_mod)

                if len(match) != 0:
                    if match[0] in result.keys():
                        result[match[0]] += ", " + match_2[0].rstrip().strip().lower()
                    else:
                        result[match[0]] = match_2[0].rstrip().strip().lower()

        return result

    @staticmethod
    def find_os_contents(pdf_reader):
        result = {}
        start_page = 22
        end_page = 28
        end_page = min(end_page, len(pdf_reader.pages))
        contents_page = ""
        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            lines = page_text.split('\n')
            page_text = ' '.join(lines)
            contents_page += page_text
        if not contents_page:
            return "Specified pages not found in the PDF"

        matches = re.findall(r"(\d+\.\d+)\s+(.*?)\s+(\d+)", contents_page)
        for i in matches:
            unit = i[0].split(".")[0]
            if unit not in result.keys():
                result[unit] = i[1]
            else:
                result[unit] += ", " + i[1]
        return result

    @staticmethod
    def find_hci_contents(pdf_reader, start_page, end_page):
        result = {}
        end_page = min(end_page, len(pdf_reader.pages))

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                line = (line.replace("-", " ")
                        .replace(",", "")
                        .replace(":", "")
                        .replace(";", "")
                        .replace("/", " ")
                        .replace("&", " ")
                        .replace('"', "")
                        .replace("'", "")
                        .replace("(", "")
                        .replace(")", ""))
                match = re.findall(r"(\d+)[.]*\d*[.]*\d*\s+[a-zA-Z]*", line)
                line_mod = (line.replace(".", "")
                                .replace("’", " ")
                                .replace("?", "")
                                .replace("“", "")
                                .replace("”", "")
                                .replace("#", "")
                                .replace("!", ""))
                match_2 = re.findall(r"\d+[.]*\d*[.]*\d*([a-zA-Z|\s]+)", line_mod)

                if len(match) != 0:
                    if match[0] in result.keys():
                        result[match[0]] += ", " + match_2[0].rstrip().strip().lower()
                    else:
                        result[match[0]] = match_2[0].rstrip().strip().lower()

        return result

    @staticmethod
    def find_js_contents(pdf_reader, start_page, end_page):
        result = {}
        end_page = min(end_page, len(pdf_reader.pages))
        number = None

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                line = (line.replace("-", " ")
                        .replace(",", "")
                        .replace(":", "")
                        .replace(";", "")
                        .replace("/", " ")
                        .replace("&", " ")
                        .replace('"', "")
                        .replace("'", "")
                        .replace("(", "")
                        .replace(")", ""))
                match = re.findall(r"Chapter\s*(\d+)", line)
                line_mod = (line.replace(".", "")
                                .replace("’", " ")
                                .replace("?", "")
                                .replace("“", "")
                                .replace("”", "")
                                .replace("#", "")
                                .replace("!", ""))
                match_2 = re.findall(r"\d+\s+([a-zA-Z|\s]+)", line_mod)
                match_3 = re.findall(r"\s*([a-zA-Z|\s]+)", line_mod)

                if len(match) != 0:
                    number = match[0]
                    result[number] = match_2[0].rstrip().strip().lower()
                else:
                    if len(match_2) == 0 and len(match) == 0 and len(match_3) != 0 and number is not None:
                        result[number] += ", " + match_3[0].rstrip().strip().lower()

        return result

    @staticmethod
    def find_network_contents(pdf_reader, start_page, end_page):
        result = {}
        result_2 = []

        end_page = min(end_page, len(pdf_reader.pages))
        number = None

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                line = (line.replace("-", " ")
                        .replace(",", "")
                        .replace(":", "")
                        .replace(";", "")
                        .replace("/", " ")
                        .replace("&", " ")
                        .replace('"', "")
                        .replace("'", "")
                        .replace("(", "")
                        .replace(")", ""))

                match = re.findall(r"Chapter\s+(\d+)\s+[a-zA-Z|\s]+", line)

                line_mod = line.replace("’", " ").replace("?", "").replace("“", "").replace("”", "")

                result_2.append(line_mod.lower())

                line_mod = line_mod.replace(".", " ")

                match_2 = re.findall(r"Chapter\s+\d+\s+([a-zA-Z|\s]+)", line_mod)
                match_subsections_2 = re.findall(r"\d+\s\d+\s+\d*\s*([a-zA-Z|\s]+)", line_mod)
                if len(match) != 0:
                    result[match[0]] = match_2[0].rstrip().strip().lower()
                    number = match[0]
                elif len(match_subsections_2) != 0 and number is not None:
                    result[number] += ", " + match_subsections_2[0].rstrip().strip().lower()

        return result

    @staticmethod
    def find_robot_os_contents(pdf_reader, start_page, end_page):
        result = {}
        end_page = min(end_page, len(pdf_reader.pages))
        number = None

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                line = (line.replace("-", " ")
                        .replace(",", "")
                        .replace(":", "")
                        .replace(";", "")
                        .replace("/", " ")
                        .replace("&", " ")
                        .replace('"', "")
                        .replace("'", "")
                        .replace("(", "")
                        .replace(")", ""))

                match = re.findall(r"Chapter\s+(\d+)\s+[a-zA-Z|\s]+", line)
                line_mod = line.replace(".", " ").replace("’", " ").replace("?", "").replace("“", "").replace("”", "")
                match_2 = re.findall(r"Chapter\s+\d+\s+([a-zA-Z|\s]+)", line_mod)
                match_subsections = re.findall(r"\s*([a-zA-Z|\s]+)", line)

                if len(match) != 0:
                    result[match[0]] = match_2[0].rstrip().strip().lower()
                    number = match[0]
                elif len(match_subsections) != 0 and number is not None:
                    result[number] += ", " + match_subsections[0].rstrip().strip().lower()

        return result

    @staticmethod
    def find_robotic_python_content(pdf_reader, start_page, end_page):
        result = {}
        end_page = min(end_page, len(pdf_reader.pages))
        number = None

        for page_num in range(start_page, end_page):
            page_text = pdf_reader.pages[page_num].extract_text()
            for line in page_text.split("\n"):
                line = (line.replace("-", " ")
                        .replace(",", "")
                        .replace(":", "")
                        .replace(";", "")
                        .replace("/", " ")
                        .replace("&", " ")
                        .replace('"', "")
                        .replace("'", "")
                        .replace("(", "")
                        .replace(")", ""))

                match = re.findall(r"Chapter\s+(\d+)\s+[a-zA-Z|\s]+", line)
                line_mod = line.replace(".", " ").replace("’", " ").replace("?", "").replace("“", "").replace("”", "")
                match_2 = re.findall(r"Chapter\s+\d+\s+([a-zA-Z|\s]+)", line_mod)
                match_subsections = re.findall(r"\s*([a-zA-Z|\s]+)", line)
                if len(match) != 0:
                    result[match[0]] = match_2[0].rstrip().strip().lower()
                    number = match[0]
                elif len(match_subsections) != 0 and number is not None:
                    result[number] += ", " + match_subsections[0].rstrip().strip().lower()

        return result