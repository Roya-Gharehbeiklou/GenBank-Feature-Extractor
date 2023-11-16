"""
GenebankParser class
Auther: Roya Gharehbeiklou
Date: 06/11/2022
"""
import re
from typing import List
from feature import Feature


class GenbankParser:
    """
    This class parse the files of mRNA, DNA and protein.
    Then, the features that are mentioned in files, are extracted.
    As the last step, the reaults are written to the output file.

    to initialize the class,
    input_filename: The path of mRNA, DNA and protein file.
    output_filename: The path of output file.
    is_uppercase: True if uppercase mode is selected
                  False is used for seperated mode

    parse_operation method is used to do all the steps in order.

    Rest of methods are defined for the class only(private mode)
    """

    def __init__(self, input_filename, output_filename, is_uppercase):
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.sequence_info = ""
        self.features: List[Feature] = []
        self.definition_section = ""
        self.is_uppercase = is_uppercase

    def parse_operation(self):
        """
        This function does the steps in order
        """
        self.file_reader()
        self.feature_analyze()
        self.file_writer()

    def file_reader(self):
        """
        This function read the file line by line
            to extract features and origins
        """
        with open(self.input_filename, 'r', encoding="utf-8") as input_file:
            line_num = 0
            # To know which part is parsing
            feature_section = False
            origin_section = False
            feature_data = ""
            feature_name = ""

            for line in input_file:
                # Find sections of input file
                if line.startswith("DEFINITION"):
                    self.definition_section = line[11:].strip()
                    continue
                if line.startswith("FEATURES"):
                    feature_section = True
                    # Skip process of analysing this line,
                    # the selected section(features) has found
                    continue
                if line.startswith("ORIGIN"):
                    feature_section = False
                    origin_section = True
                    continue

                # Process each section of input file
                if feature_section:
                    # Check whather there are five spaces before a name
                    # and consider it as a new feature
                    # and add it to features objects list
                    match = re.search(
                        r"^[ ]{5}(?P<name>\w+)\s+(?P<data>.+)",
                        line)

                    if match:
                        try:
                            matches = match.groupdict()
                            feature_name = matches['name']
                            feature_data = matches['data'].strip().strip("\n")
                            self.features.append(
                                Feature(feature_name, feature_data)
                            )
                        except Exception as ex:
                            raise Exception(
                                f'Input file format is not correct in line '
                                f'{line_num}, {ex}') from ex
                    else:
                        # All the lines apeared after feature name in file
                        # And add the line to the last feature data
                        # which was added to the list previously
                        # \n and spaces are removed
                        try:
                            feature_info = line.strip().strip('\n')
                            self.features[-1].featur_data += feature_info
                        except Exception as ex:
                            raise Exception(
                                f'Input file format is not correct in line '
                                f'{line_num}, {ex}') from ex

                if origin_section:
                    # removing all the spaces and numbers of shown
                    # in each line and \n in the origin
                    try:
                        data = line[10:].replace(' ', '').strip('\n')
                        self.sequence_info += data
                    except Exception as ex:
                        raise Exception(
                            f'Input file format is not correct in line '
                            f'{line_num}, {ex}') from ex

                line_num += 1

    def feature_analyze(self):
        """
        This function analyse per feature in features object list
        """
        for feature in self.features:
            positions, definition, is_complement = self.feature_data_parse(
                feature.featur_data
            )
            feature.feature_positions_set(positions)
            feature.feature_complement_set(is_complement)
            feature.feature_definition_set(definition)

    def feature_data_parse(self, feature_data):
        """
        This function parses each feature data extracted from file
        that are seperated by charater '/' in order to extract positions
        and definition of each feature

        Args:
            feature_data (str): extracted feature info from file
        Raises:
            Exception: Exception when try to parse positions

        Returns:
            final_positions [(int, int), ...]: positions that
                must be read from the sequence
            feature_definition (str): description of feature
            is_complement (boolean) : To be complemented or not
        """
        is_complement = False
        final_positions = []
        feature_definition = ""

        # The first part of feature data contains feature positions info
        data_positions = feature_data.split("/")[0]
        # The second part is consist of feature definition
        feature_definition = "/" + feature_data.split("/")[1]

        # Order expression has the same treatment as join expression
        # It was replaced by join
        if 'order' in data_positions:
            data_positions = data_positions.replace("order", "join")

        # check whether feature position contains complement expression or not
        find_complement = re.search(
            r"complement\((?P<position>.*)\)",
            data_positions)
        if find_complement:
            data_positions = find_complement["position"]
            is_complement = True

        # check whether feature position contains complement expression or not
        find_join = re.search(r"join\((?P<position>.*)\)", data_positions)
        if find_join:
            data_positions = find_join["position"].split(",")
        if isinstance(data_positions, str):
            data_positions = [data_positions]

        # This loop find and store these kinds of positions(1..50,60..80)
        for data_position in data_positions:
            positions = re.split(r"\.+>?", data_position)
            if len(positions) == 2:
                start_position = int(positions[0])
                end_position = int(positions[1])
                final_positions.append((start_position, end_position))
            elif len(positions) == 1:
                start_position = int(positions[0])
                end_position = None
                final_positions.append((start_position, end_position))
            else:
                raise Exception("Exception when try to parse positions")

        return final_positions, feature_definition, is_complement

    def file_writer(self):
        """
        This function write what ever we had parsed
            according to the format of genebank output
        """
        uppercased = self.is_uppercase

        with open(self.output_filename, 'w', encoding="utf-8") as output_file:
            output_file.write(self.definition_section + "\n\n")

            for feature in self.features:
                # write feature name
                output_file.write(f">{feature.feature_name} "
                                  f"{feature.feature_definition}\n")

                # join feature data acording to uppercase or seperated mode
                data_position = ""
                for index, position in enumerate(feature.positions):
                    if uppercased:
                        current_position = position
                        previous_position = None
                        if index > 0:
                            previous_position = feature.positions[index - 1]
                        data_uppercase = self.get_data_betwean_two_position(
                            previous_position, current_position)
                        data_position += data_uppercase
                    data_normal = self.get_sequence_by_position(
                        position[0],
                        position[1])
                    if uppercased:
                        data_normal = data_normal.upper()
                    data_position += data_normal
                if feature.is_complement:
                    data_position = self.get_complement_sequence(data_position)
                lines = self.break_data_into_lines(data_position)

                for line in lines:
                    output_file.write(line)
                output_file.write("\n")

    def get_sequence_by_position(self, start_position, end_position):
        """
        This function read the sequences to recognize start and end positions

        Args:
            start_position (str): Start position
            end_position (str): End position and
                it may be None when only one position is set

        Returns:
            data (str): The positions
        """
        if end_position is not None:
            data = self.sequence_info[start_position - 1: end_position]
        else:
            data = self.sequence_info[start_position - 1]
        return data

    def get_data_betwean_two_position(
            self,
            previous_position,
            current_position):
        """
        This function returns sequenced data between two positin,
        if previous_position is set to None returns data from start of sequence
        if previous_position does not have end value, the start value is used
            the position was a single position when it parsed

        Args:
        previous_position (int, int) or None: (start, end) of previous position
        current_position (int, int) : (start, end) of curent positon

        Returns:
            data_sequence str: sequence between two positon
        """

        start = 1
        if previous_position is not None:
            if previous_position[1] is not None:
                start = previous_position[1] + 1
            else:
                start = previous_position[0] + 1

        end = current_position[0] - 1
        data_sequence = self.get_sequence_by_position(start, end)

        return data_sequence

    def get_complement_sequence(self, sequence_data):
        """
        This function replaces the bases in order to be complemented

        Args:
            sequence_data (str): Gene sequence

        Returns:
            complement_sequence (str): Data complemented
        """
        dict_complement = {"c": "g", "g": "c", "t": "a", "a": "t",
                           "C": "G", "G": "C", "T": "A", "A": "T"}
        complement_sequence = ""
        for item in sequence_data[::-1]:
            complement_sequence += dict_complement[item]

        return complement_sequence

    def break_data_into_lines(self, text_data):
        """
        This function prepare the data to be written in the output file.
        Data is seperated into 60 length of characters due to the format given

        Args:
            text_data (str): lines of genes

        Returns:
            lines(str): list of strings with the length of 60 characters
        """
        lines = []
        for i in range(0, len(text_data), 60):
            line = f"{text_data[i: i + 60]}\n"
            lines.append(line)

        return lines
