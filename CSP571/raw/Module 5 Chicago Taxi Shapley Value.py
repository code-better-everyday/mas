"""
Name: Module 5 Chicago Taxi Shapley Value.py
Course: Data Preparation and Analysis
Created Date: November 5, 2023
Author: Ming-Long Lam, Ph.D.
Organization: Illinois Institute of Technology
"""

import numpy
import pandas
import sys

from scipy.special import comb
from itertools import (chain, combinations)

sys.path.append('C:\\IIT\\Data Preparation and Analysis\\Code')
import Utility

# Set some options for printing all the columns
numpy.set_printoptions(precision = 10, threshold = sys.maxsize)
numpy.set_printoptions(linewidth = numpy.inf)

pandas.set_option('display.max_columns', None)
pandas.set_option('display.expand_frame_repr', False)
pandas.set_option('max_colwidth', None)

pandas.options.display.float_format = '{:,.10f}'.format

TaxiTrip = pandas.read_csv('C:\\IIT\\Data Preparation and Analysis\\Data\\Twenty_Chicago_Taxi_Trip.csv', delimiter = ',')

categorical_feature = ['Payment_Method']
continuous_feature = ['Trip_Minutes', 'Trip_Miles']
target_name = 'Trip_Payment'

train_data = TaxiTrip[[target_name] + categorical_feature + continuous_feature]

# Note: there are no missing values in the training data
print('=== Number of Missing Values Per Variable ===')
print(numpy.sum(train_data.isna()))

n_sample = train_data.shape[0]

# Generate a dataframe that contains the all-possible model specifications

candidate = categorical_feature + continuous_feature
n_candidate = len(candidate)
feature_position = []
for i in range(n_candidate):
   feature_position.append('POS_' + str(i))

all_model_spec = pandas.DataFrame(chain(*map(lambda x: combinations(candidate, x), range(0, n_candidate+1))),
                                  columns = feature_position)

n_feature_list = []
model_df_list = []
sse_list = []

# Generate the full model matrix and remember each candidate's columns in the full model matrix

X_all = train_data[[]].copy()
X_all.insert(0, 'Intercept', 1.0)

start_column = 0
last_column = 0

component_column = {}
for pred in candidate:
   X_term = train_data[[pred]]
   if (numpy.isin(pred, categorical_feature)):
      X_term = pandas.get_dummies(X_term, dtype = float)
   X_all = X_all.join(X_term)
   start_column = last_column + 1
   last_column = start_column + X_term.shape[1] - 1
   component_column[pred] = [j for j in range(start_column, last_column+1)]

# Train all the model specifications
y = train_data[target_name] 

for idx, row in all_model_spec.iterrows():
   model_column = [0]
   n_feature = 0
   for pos in feature_position:
      pred = row[pos]
      if (pred is not None):
         n_feature = n_feature + 1
         model_column = model_column + component_column[pred]
      else:
         break
   X = X_all.iloc[:, model_column]
   result_list = Utility.LinearRegressionModel (X, y)
   model_df = len(result_list[5])
   SSE =  result_list[2] * result_list[3]

   if (n_feature == 0):
      SST = SSE

   n_feature_list.append(n_feature)
   model_df_list.append(model_df)
   sse_list.append(SSE)

all_model_spec['N_Feature'] = n_feature_list
all_model_spec['Model DF'] = model_df_list
all_model_spec['RSquare'] = 1.0 - sse_list / SST

# Make the model specifications as a Python set

model_k_spec = {}
for k in range(0, n_candidate+1):
   subset = all_model_spec[all_model_spec['N_Feature'] == k]
   out_list = []
   for idx, row in subset.iterrows():
      cur_rsq = row['RSquare']
      cur_set = set(list(row[feature_position].dropna()))
      out_list.append([cur_set, cur_rsq])
   model_k_spec[k] = pandas.DataFrame(out_list, columns = ['FeatureSet','RSquare'])

# Find the nested mdoels and calculate the R-Square changes

result_list = []
for k in range(0,n_candidate,1):
   spec_0 = model_k_spec[k]
   spec_1 = model_k_spec[k+1]
   for idx_0, row_0 in spec_0.iterrows():
      set_0 = row_0['FeatureSet']
      rsq_0 = row_0['RSquare']
      for idx_1, row_1 in spec_1.iterrows():
         set_1 = row_1['FeatureSet']
         rsq_1 = row_1['RSquare']
         set_diff = set_1.difference(set_0)
         print(set_0, set_1, set_diff, len(set_diff))
         if (len(set_diff) == 1):
            rsq_diff = rsq_1 - rsq_0
            wgt = (n_candidate - 1) / comb((n_candidate-1), k)
            result_list.append([k, list(set_diff)[0], rsq_diff, wgt])

result_df = pandas.DataFrame(result_list, columns = ['k', 'Feature', 'RSqChange', 'Wgt'])

# Calculate the Shapley values

def weighted_average(df, values, weights):
    return sum(df[weights] * df[values]) / df[weights].sum()

shapley = result_df.groupby('Feature').apply(weighted_average, 'RSqChange', 'Wgt')
total_shapley = numpy.sum(shapley)
percent_shapley = 100.0 * (shapley / total_shapley)
print(' Sum of Shapley Values = ', total_shapley)

# Check if the sum of Shapley values is equal to the Full Model's R-Square

subset = all_model_spec[all_model_spec['N_Feature'] == n_candidate]
print('R-Square of Full Model = ', subset['RSquare'].values[0])
