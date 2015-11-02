__author__ = "Charlie"


import importlib
import data_manager
import config
import numpy as np
from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline


def load_config():
	"""
	Prompts for user config choice, loads and returns config module.

	@return: config module
	"""
	for i, c in enumerate(config.__all__):
		print("[{}] {}".format(i, c))
	inp = input("Select your run configurations.\n>>>")
	return importlib.import_module("config." + config.__all__[i])


def load_dataset():
	"""
	Simple data set load implementation.
	This will be moved to a file called data_manager.py that
	should handle loading and vectorizing.

	@return: np.matrix, np,array
	"""
	load_functions = []
	for i, (dataset_name, load_function) in enumerate(data_manager.available_datasets()):
		load_functions.append(load_function)
		print("[{}] {}".format(i, dataset_name))
	inp = input("Select your dataset.\n>>>")
	X, y = load_functions[i]()
	return X, y


def build_pipelines(configuration):
	"""
	"""
	pipelines = []
	for learner_tup, learner_params in configuration.learners.items():
		for selector_tup, selector_params in configuration.selectors.items():
			learner_name = learner_tup[0]
			learner = learner_tup[1]
			selector_name = selector_tup[0]
			selector = selector_tup[1]
			pipe = Pipeline([
				(selector_name, selector), 
				(learner_name, learner)
			])
			params = dict(learner_params, **selector_params)
			pipelines.append((pipe, params))
	return pipelines


def execute_configuration(configuration, X, y):
	"""
	"""
	for pipeline, params in build_pipelines(configuration):
		grid = GridSearchCV(pipeline, params, cv=10)
		grid.fit(X, y)
		for score in grid.grid_scores_:			
			print(score.parameters, \
				'[Mean]          = %5.4f%%' % score.mean_validation_score, \
				'[Std Deviation] = %5.4f%%' % np.std(score.cv_validation_scores))


def main():
	"""
	Main program loop
	"""
	running = True

	while running:
		X, y = load_dataset()
		configuration = load_config()
		execute_configuration(configuration, X, y)
		running = prompt


if __name__ == '__main__':
	main()
