"""
final.py
Auther: Roya Gharehbeiklou
Date: 06/11/2022
Example: python3 final.py CFTR_mRNA.gb False
"""
import sys
from genebank_parser import GenbankParser

def get_output_filename(input_file_name: str) -> str:
    """
     This function takes the name of input file and generate the name of output file

        Args:
            input_file_name (str): name of the file which is entered by user

        Returns:
            output_file_name (str): name of output file
    """
    # name of output file
    if (not input_file_name.endswith(".gb")
            and not input_file_name.endswith(".gp")):
        raise Exception('The format of the file is not correct')

    # check the format
    if input_file_name.endswith(".gb"):
        output_file_name = input_file_name.replace('.gb', '_feature.txt')
    if input_file_name.endswith(".gp"):
        output_file_name = input_file_name.replace('.gp', '_feature.txt')

    print(f'input name : {input_file_name} output name: {output_file_name}')

    return output_file_name


def main():
    """
    This function is used to get a file from user by command line
        which the user is choosing the mode of the output(seperated/uppercase)
        by boolean value
    """
    # name of input file
    input_filename = sys.argv[1]
    # uppercase option boolean, default value is False
    uppercase = False
    if sys.argv[2] == "True":
        uppercase = True

    # check the file format
    output_filename = get_output_filename(input_filename)
    parser = GenbankParser(input_filename, output_filename, uppercase)
    parser.parse_operation()

if __name__ == "__main__":
    main()
