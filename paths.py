import math
import argparse

class Case():
	""" A class that manages the paths for a case in the input file. """

	def __init__(self, case_number):
		""" Constructor for the Case Class.
		
		Args:
			case_number (str): the case number (e.g. "Case 1")
		"""
		self.case_number = case_number

		#: set of Location objects
		self.locations = set()

		#: tupple with objective details
		self.objective = None


	def set_objective(self, bars, start_location, end_location):
		""" Sets the objective for a case.
		
		Args:
			bars (int): the number of bars to be transported
			start_location (Location Obj): The start location
			end_location (Location Obj): The final location
		"""
		self.objective = (bars, start_location, end_location)


	def get_objective(self):
		""" Returns the objective tupple """
		return self.objective


	def add_location(self, location):
		""" Adds a location to the set of location objects.
	
		Args:
			location (Location Obj): A location object
		"""
		self.locations.add(location)


	def get_locations(self):
		""" Returns the set of location objects """
		return self.locations


	def get_name(self):
		""" Returns the case number string """
		return self.case_number

	def __str__(self):
		""" Returns the case number string """
		return self.case_number


	def possible_paths(self, start_location, end_location, path=[]):
		""" Returns a list of possible paths, using the locations and their
		connections.

		Args:
			start_location (Location Obj): the start location
			end_location (Location Obj): The final location
			path (list): list of location objects to be passed recursively

		"""
		paths = []
		path = path + [start_location]
		if start_location == end_location:
			return [path]
		if len(start_location.get_connected_location()) == 0:
			return []

		for next_loc in start_location.get_connected_location():
			next_path = self.possible_paths(next_loc, end_location, path)
			for p in next_path:
				paths.append(p)

		return paths


class Location():
	""" A class that represents a location """

	def __init__(self, name, loc_type):
		""" The constructor for the Location Object.

		Args:
			name (str): the name of the location
			loc_type (str): the type of location (town or village)
		"""
		self.name = name
		self.loc_type = loc_type

		#: list of connected Location objects to the this object
		self.connected = []


	def get_name(self):
		""" Returns the Location's name """
		return self.name


	def add_connected_location(self, location):
		""" Adds a Location Object to the list of connected locations.
		
		Args:
			location (Location Obj): A location object.
		"""
		self.connected.append(location)


	def get_connected_location(self):
		""" Returns the list of connected locations """
		return self.connected


	def get_type(self):
		""" Returns the Location type """
		return self.loc_type


	def __str__(self):
		""" Returns the Location's name """
		return self.name


def read_input(file):
	""" Receives an input file to be processed into a more readable format.
	Returns the 

	Args:
		file (str): The string for the input file to be processed

	"""
	input_file = open(file).readlines()
	i = 1
	cases = {}
	case_details = [set(), set()]  # [ set(locations), set(roads)]

	for line in input_file:
		continue_flag = True
		items = line.strip().split("\t")

		# Cases
		if len(items) == 1 and int(items[0]) != -1:
			case_details = [set(), set()]
			cases["Case {}".format(i)] = case_details
			i += 1

		# Location and roads
		if len(items) == 2:
			starting_place = items[0]
			delivery_place = items[1]
			cases["Case {}".format(i - 1)][0].add(starting_place)
			cases["Case {}".format(i - 1)][0].add(delivery_place)
			cases["Case {}".format(
				i - 1)][1].add(starting_place + delivery_place)

		# Delivery Details
		if len(items) == 3:
			number_of_bars = items[0]
			starting_place = items[1]
			delivery_place = items[2]
			cases["Case {}".format(
				i - 1)].append((number_of_bars, starting_place, delivery_place))

	return cases


def process_cases(case_dict):
	""" Receives the dictionary of cases from the read_input function and
	processes it into Objects, creating a Case object for each case and a
	Location object for each location.

	args:
		case_dict (dict): A dictionary of cases, locations and paths.
	"""
	cases = []
	for case in case_dict:
		location_dict = {}
		create_case = Case(case)

		for location in case_dict[case][0]:
			location_type = "village"
			if location.islower():
				location_type = "town"

			create_location = Location(location, location_type)
			create_case.add_location(create_location)
			location_dict[location] = create_location

		for roads in case_dict[case][1]:
			start = roads[0]
			end = roads[1]
			location_dict[start].add_connected_location(location_dict[end])

		objective = case_dict[case][2]
		create_case.set_objective(int(objective[0]), location_dict[
								  objective[1]], location_dict[objective[2]])

		cases.append(create_case)

	return cases


def calculate_price(path, bars_transported):
	""" Calculates the number of bars necessary for a given path. 
	Returns a tupple with the path and the total necessary bars.

	args:
		path (list): List of locations from the start location to the
	end location.
		bars_transported (int): Number of bars to be transported.
	"""
	town_count = 0
	village_count = 0
	for i in range(1, len(path)):
		if path[i].get_type() == "town":
			town_count += 1
		if path[i].get_type() == "village":
			village_count += 1
	total_bars = bars_transported + town_count + \
		int(math.ceil(bars_transported / 20.0)) * village_count

	if int(math.ceil(total_bars / 20.0)) > total_bars / 20:
		total_bars = total_bars + village_count

	return (path, total_bars)


def write_output(output_file, best_cases_dict):
	""" Writes in a file the results of the best paths for each case.

	args:
		file (str): the string for the output file name
		best_cases_dict: a dictionary with the best path for each case
	"""
	output_file = open(output_file, "w")

	for key in sorted(best_cases_dict.keys()):
		output_file.write(key + ": " + str(best_cases_dict[key]) + "\n")

	output_file.close()


def main():
	parser = argparse.ArgumentParser(description='Chepeast Path')
	parser.add_argument(
		'-i', '--input', help='Path to input file" ', type=str, dest="input")
	parser.add_argument(
		'-o', '--output', help='Path to input file" ', type=str, dest="output")
	args = parser.parse_args()

	if not args.input:
		print "No input file inserted."
	if not args.output:
		print "No output file inserted."

	if args.input and args.output:
		case_dict = read_input(args.input)
		cases = process_cases(case_dict) # {'Case 2': None, 'Case 1': None}
		best_cases = {b.get_name(): None for b in cases}

		for case in cases:
			objective = case.get_objective()
			paths = case.possible_paths(objective[1], objective[2])
			best = ([], 9999)
			for path in paths:
				new = calculate_price(path, objective[0])
				print "{} - Possible Path check: {}, Number of required bars: {}".format(case.get_name(), str([x.get_name() for x in path]), str(new[1]))
				if new[1] < best[1]:
					best = new
			best_cases[case.get_name()] = best[1]
		write_output(args.output, best_cases)

if __name__ == '__main__':
	main()


# Location
