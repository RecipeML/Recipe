# -*- coding: utf-8 -*-

"""
Copyright 2016 Walter José

This file is part of the RECIPE Algorithm.

The RECIPE is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

RECIPE is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. See http://www.gnu.org/licenses/.

"""

import warnings

from sklearn.preprocessing import LabelEncoder

import numpy as np
import pandas as pd

import load_pipeline as load
from sklearn.pipeline import make_pipeline
from sklearn import cross_validation

import resource

def evaluate_algorithm(mlAlgorithm, dataTraining, seed, dataSeed, internalCV,metric):

	"""Evaluate a single algorithm

    Parameters
    ----------

   	mlAlgorithm: string
        is the pipeline that will be evaluated.

    dataTraining:
        The data used to train the choosen method.

    seed: int
        The seed used to control the GP behaviour.

    dataSeed:int
        The seed to control the data resample each x generations.

    internalCV: int
        The number of folds in the internal cross-validation procedure.

    """

	# soft, hard = 2147483648, 2147483648
	# resource.setrlimit(resource.RLIMIT_AS,(soft, hard))

	try:
		#Load the dataset:
		df = pd.read_csv(dataTraining, header=0, delimiter=",")

		class_name = df.columns.values.tolist()[-1]

		#Apply a filter if the data has categorical data (sklean does not accept this type of data):
		objectList = list(df.select_dtypes(include=['object']).columns)
		if (class_name in objectList and len(objectList)>=1):
			df = df.apply(LabelEncoder().fit_transform)

		#Set the trainining data and target (classes):
		training_data = df.ix[:,:-1].values

		training_target = df[class_name].values

		pipe = load.load_pipeline(mlAlgorithm)

		#Verify if the pipeline is valid. Otherwise, return 0.0 as evaluation
		try:
			pipeline=make_pipeline(*pipe)
		except Exception as exc:
			warnings.warn(exc, "->", mlAlgorithm,UserWarning)
			return 0.0

		#To shuffle data in the cv according to the dataSeed:
		n_samples = training_data.shape[0]
		cv = cross_validation.ShuffleSplit(n_samples, n_iter=internalCV, train_size=0.67,
			test_size=0.33, random_state=dataSeed)

		#Fit the final model generated by the pipeline:
		scores = cross_validation.cross_val_score(pipeline, training_data, training_target,
			cv=cv, scoring=metric)

		result = scores.mean()

		return result
	except (KeyboardInterrupt, SystemExit):
		return 0.0
	except Exception as e:
		warnings.warn("WARNING: "+ str(e) + "->" + mlAlgorithm,UserWarning)
		return 0.0
