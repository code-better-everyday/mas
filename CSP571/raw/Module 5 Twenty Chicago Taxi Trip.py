"""
Name: Module 5 Twenty Chicago Taxi Trip.py
Course: Data Preparation and Analysis
Created Date: November 5, 2023
Author: Ming-Long Lam, Ph.D.
Organization: Illinois Institute of Technology
"""

import matplotlib.pyplot as plt
import numpy
import pandas
import sys

from scipy.stats import f

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

fig, (ax00, ax01) = plt.subplots(1, 2, dpi = 1200, sharey = True, figsize = (9,4))
plt.subplots_adjust(wspace = 0.1)

ax00.scatter(TaxiTrip['Trip_Minutes'], TaxiTrip['Trip_Payment'])
ax00.set_xlabel('Trip Number of Minutes')
ax00.set_ylabel('Trip Payment ($)')
ax00.set_xticks(range(20,60,5))
ax00.set_yticks(range(25,60,5))
ax00.grid(axis = 'both')

ax01.scatter(TaxiTrip['Trip_Miles'], TaxiTrip['Trip_Payment'])
ax01.set_xlabel('Trip Number of Miles')
ax01.set_xticks(range(10,24,2))
ax01.set_yticks(range(25,60,5))
ax01.grid(axis = 'both')

plt.show()

# Model is Trip_Payment = Intercept + Trip_Minutes + Trip_Miles
X = TaxiTrip[['Trip_Minutes', 'Trip_Miles']]
X.insert(0, 'Intercept', 1)
y = TaxiTrip['Trip_Payment']
result_list = Utility.LinearRegressionModel (X, y)

# Label the output properly
parameter_table = result_list[0]

# Calculate the predicted value
y_predicted = X.dot(parameter_table['Estimate'])

# Plot predicted versus observed
plt.figure(figsize = (8,6), dpi = 200)
plt.scatter(y, y_predicted, marker = 'o')
plt.xlabel('Observed Trip Payment ($)')
plt.ylabel('Predicted Trip Payment ($)')
plt.xlim((25,55))
plt.ylim((25,55))
plt.axline((40.0,40.0), slope = 1.0, linestyle = '--', color = 'red')
plt.grid()
plt.show()

# Plot residual versus observed
residual = y_predicted - y
plt.figure(figsize = (8,6), dpi = 200)
plt.scatter(y, residual, marker = 'o')
plt.xlabel('Observed Trip Payment ($)')
plt.ylabel('Residual ($)')
plt.xlim((25,55))
plt.axhline(0.0, linestyle = '--', color = 'red')
plt.grid()
plt.show()

# Model is Trip_Payment = Intercept + Payment_Method + Trip_Minutes + Trip_Miles
cash_data = TaxiTrip[TaxiTrip['Payment_Method'] == 'Cash']
card_data = TaxiTrip[TaxiTrip['Payment_Method'] == 'Credit Card']

fig, (ax00, ax01) = plt.subplots(1, 2, dpi = 1200, sharey = True, figsize = (9,4))
plt.subplots_adjust(wspace = 0.05)

s0 = ax00.scatter(cash_data['Trip_Minutes'], cash_data['Trip_Payment'], c = 'red')
s1 = ax00.scatter(card_data['Trip_Minutes'], card_data['Trip_Payment'], c = 'blue')
ax00.set_xlabel('Trip Number of Minutes')
ax00.set_ylabel('Trip Payment ($)')
ax00.set_xticks(range(20,60,5))
ax00.set_yticks(range(25,60,5))
ax00.grid(axis = 'both')

ax01.scatter(card_data['Trip_Miles'], card_data['Trip_Payment'], c = 'blue')
ax01.scatter(cash_data['Trip_Miles'], cash_data['Trip_Payment'], c = 'red')
ax01.set_xticks(range(10,24,2))
ax01.set_yticks(range(25,60,5))
ax01.set_xlabel('Trip Number of Miles')
ax01.grid(axis = 'both')

fig.legend([s0,s1], ['Cash','Credit Card'], loc = 'upper center', ncol = 2)
plt.show()

# Forward Selection
catName = ['Payment_Method']
intName = ['Trip_Miles', 'Trip_Minutes']
yName = 'Trip_Payment'

train_data = TaxiTrip[catName + intName + [yName]]
n_sample = train_data.shape[0]

step_diary = []
y_train = train_data[yName]
                    
# Intercept only model
X0_train = train_data[[]].copy()
X0_train.insert(0, 'Intercept', 1.0)

result_list = Utility.LinearRegressionModel (X0_train, y_train)
sse0 = result_list[2] * result_list[3]
m0 = len(result_list[5])

step_diary.append([0, 'Intercept', ' ', m0, sse0, numpy.nan, numpy.nan, numpy.nan])

entryThreshold = 0.05

cName = catName.copy()
iName = intName.copy()
nPredictor = len(cName) + len(iName)

# The Deviance significance is the eighth element in each row of the test result
def takeDevSig(s):
    return s[7]

for step in range(nPredictor):
    enterName = ''

    # Columns are 'Predictor', 'Type', 'N Iter', 'ModelDF', 'ModelLLK', 'DevChiSq', 'DevDF', 'DevSig'
    step_detail = []

    # Enter the next predictor
    for X_name in cName:
        X_train = X0_train.join(pandas.get_dummies(train_data[[X_name]].astype('category'), dtype = float))
        result_list = Utility.LinearRegressionModel (X_train, y_train)
        sse1 = result_list[2] * result_list[3]
        m1 = len(result_list[5])
        df_numer = m1 - m0
        df_denom = n_sample - m1
        FStat = ((sse0 - sse1) / df_numer) / (sse1 / df_denom)
        FSig = f.sf(FStat, df_numer, df_denom)
        step_detail.append([X_name, 'categorical', m1, sse1, FStat, df_numer, df_denom, FSig])

    for X_name in iName:
        X_train = X0_train.join(train_data[[X_name]])
        result_list = Utility.LinearRegressionModel (X_train, y_train)
        sse1 = result_list[2] * result_list[3]
        m1 = len(result_list[5])
        df_numer = m1 - m0
        df_denom = n_sample - m1
        FStat = ((sse0 - sse1) / df_numer) / (sse1 / df_denom)
        FSig = f.sf(FStat, df_numer, df_denom)
        step_detail.append([X_name, 'interval', m1, sse1, FStat, df_numer, df_denom, FSig])

    # Find a predictor to add, if any
    step_detail.sort(key = takeDevSig, reverse = False)
    minSig = takeDevSig(step_detail[0])
    if (minSig <= entryThreshold):
        add_var = step_detail[0][0]
        add_type = step_detail[0][1]
        m0 = step_detail[0][2]
        sse0 = step_detail[0][3]
        step_diary.append([step+1] + step_detail[0])
        if (add_type == 'categorical'):
           X0_train = X0_train.join(pandas.get_dummies(train_data[[add_var]].astype('category'), dtype = float))
           cName.remove(add_var)
        else:
           X0_train = X0_train.join(train_data[[add_var]])
           iName.remove(add_var)           
    else:
        break

# End of forward selection
print('\n======= Step Summary =======')
step_diary = pandas.DataFrame(step_diary, columns = ['Step', 'Predictor', 'Type', 'ModelDF', \
                              'ModelSSE', 'F', 'DF1', 'DF2', 'DevSig'])
print(step_diary)

# Re-train final model
result_list = Utility.LinearRegressionModel (X0_train, y_train)
                                             
# Label the output properly
parameter_table = result_list[0]

# Reorder the categories of Payment_Method
u = TaxiTrip['Payment_Method'].astype('category').copy()
TaxiTrip['Payment_Method'] = u.cat.reorder_categories(['Credit Card', 'Cash'])

X0_train = TaxiTrip[['Trip_Miles']]
X0_train.insert(0, 'Intercept', 1.0)
X0_train = X0_train.join(pandas.get_dummies(TaxiTrip[['Payment_Method']].astype('category'), dtype = float))

# Re-train final model
result_list = Utility.LinearRegressionModel (X0_train, y_train)
                                             
# Label the output properly
parameter_table = result_list[0]

# Calculate the predicted value
y_predicted = X0_train.dot(parameter_table['Estimate'])

# Plot predicted versus observed
plt.figure(figsize = (8,6), dpi = 200)
plt.scatter(y, y_predicted, marker = 'o')
plt.xlabel('Observed Trip Payment ($)')
plt.ylabel('Predicted Trip Payment ($)')
plt.xlim((25,55))
plt.ylim((25,55))
plt.axline((40.0,40.0), slope = 1.0, linestyle = '--', color = 'red')
plt.grid()
plt.show()

# Plot residual versus observed
residual = y_predicted - y_train
plt.figure(figsize = (8,6), dpi = 200)
plt.scatter(y, residual, marker = 'o')
plt.xlabel('Observed Trip Payment ($)')
plt.ylabel('Residual ($)')
plt.xlim((25,55))
plt.axhline(0.0, linestyle = '--', color = 'red')
plt.grid()
plt.show()

# R-Square of the final model Trip_Payment ~ Intercept + Trip_Miles + Payment_Method
sst_y = numpy.sum(numpy.square(y_train - numpy.mean(y_train)))
sse_y = result_list[2] * result_list[3]
r_square = 1.0 - (sse_y / sst_y)

print('Coefficient of Determination = {:,.4f}'.format(r_square))