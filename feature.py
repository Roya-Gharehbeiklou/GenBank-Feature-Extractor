"""
Feature class
Auther: Roya Gharehbeiklou
Date: 06/11/2022
"""

class Feature:
    """
    This class contains five attributes for objects of feature
    """
    def __init__(self, feature_name, featur_data):
        self.feature_name = feature_name
        self.featur_data = featur_data
        self.feature_definition = ""
        #Positions is a list of (start_positon, end_positon)
        #   if there were only one position, the end_position is None
        self.positions = []
        self.is_complement = False

    def feature_definition_set(self, feature_definition):
        """
        This function is used the feature_definition variable

        Args:
            positions (str): feature_definition
        """
        self.feature_definition = feature_definition


    def feature_positions_set(self, positions):
        """
        This function is used the positions variable

        Args:
            positions (list[(int,int)]): positions
        """
        self.positions = positions

    def feature_complement_set(self, is_complement):
        """
        This function is used the is_complement variable

        Args:
            is_complement (bool): complemented or not
        """
        self.is_complement = is_complement


    def __str__(self):
        return f"fearure name is: {self.feature_name} " \
            f"and feature definition is: {self.feature_definition}"
         