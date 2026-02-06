"""
Name: Module 4 RFM Analysis.py
Course: Data Preparation and Analysis
Created Date: September 30, 2023
Author: Ming-Long Lam, Ph.D.g
Organization: Illinois Institute of Technology
"""

import matplotlib.pyplot as plt
import numpy
import pandas
import random
import sys

import seaborn
from datetime import datetime

# Set some options for printing all the columns
numpy.set_printoptions(precision = 10, threshold = sys.maxsize)
numpy.set_printoptions(linewidth = numpy.inf)

pandas.set_option('display.max_columns', None)
pandas.set_option('display.expand_frame_repr', False)
pandas.set_option('max_colwidth', None)

pandas.options.display.float_format = '{:,.10f}'.format

transaction = pandas.read_csv('C:\\IIT\\Data Preparation and Analysis\\Data\\rfm_Transactions.csv')

# Calculate Number of days since 12/31/2020

t_date = pandas.to_datetime(transaction['Date'], format='%m/%d/%Y')
reference_date = datetime.strptime('12/31/2020', "%m/%d/%Y")
n_days = pandas.Series((t_date - reference_date) / numpy.timedelta64(1, 'D'), name = 'N Days')

# Create the training data

train_data = transaction[['CustomerID', 'Date', 'Amount']].join(n_days)

# Define the aggregation procedure outside of the groupby operation
aggregations = {
    'N Days':'max',
    'CustomerID': 'count',
    'Amount': 'sum'
}

column_map = {'N Days': 'Recency', 'CustomerID': 'Frequency', 'Amount': 'Monetary'}

customer_data = train_data.groupby('CustomerID').agg(aggregations).rename(columns = column_map)
rfm_names = customer_data.columns

# Determine the quintiles
quintile = customer_data.describe(percentiles = [0.2, 0.4, 0.6, 0.8])

# Assign customers to groups
customer_group = pandas.DataFrame(numpy.where(numpy.isnan(customer_data),0,1), index = customer_data.index)

for q in ['20%','40%','60%','80%']:
   customer_group = customer_group + numpy.where(customer_data[rfm_names] > quintile.loc[q][rfm_names], 1, 0)

customer_group = customer_group.rename(columns = {0: 'Recency Score', 1: 'Frequency Score', 2: 'Monetary Score'})

# Inspect bar charts of each group
for g in ['Recency Score', 'Frequency Score','Monetary Score']:
   group_prop = 100 * customer_group[g].value_counts(ascending = True, normalize = True)

   plt.figure(figsize = (12,4), dpi = 200)
   plt.bar(group_prop.index, group_prop, color = 'royalblue')
   plt.xlabel(g)
   plt.ylabel('Percentage of Customers')
   plt.xticks(range(1,6,1))
   plt.grid(axis = 'y', linestyle = '--')
   plt.margins(y = 0.1)
   plt.show()

# Merge the group assignments back to the customer data
customer_data = customer_data.join(customer_group)

customer_data['RFM Score'] = 100 * customer_data['Recency Score'] + 10 * customer_data['Frequency Score'] + customer_data['Monetary Score']

# Look at Monetary value by Recency and Frequency groups
xtab = pandas.crosstab(index = customer_data['Recency Score'], columns = customer_data['Frequency Score'],
                       values = customer_data['Monetary'], aggfunc = 'mean')
plt.figure(figsize = (10,8), dpi = 200)
seaborn.heatmap(xtab, cmap = 'Greens', cbar_kws={'label': 'Monetary Value'})
plt.gca().invert_yaxis()
plt.show()

# Copy the RFM Score back to the transaction data
transaction_rfm = transaction.merge(customer_data['RFM Score'], left_on = ['CustomerID'], right_on = customer_data.index)

# What kind of products do the customers with RFM score 555 buy?
focus_data = transaction_rfm[transaction_rfm['RFM Score'] == 555]

product_size = focus_data['ProductLine'].value_counts(ascending = True)

plt.figure(figsize = (10,6), dpi = 200)
plt.bar(product_size.index, product_size, color = 'royalblue')
plt.yticks(range(0,100,10))
plt.xlabel('Product Line')
plt.ylabel('Number of Transactions')
plt.grid(axis = 'y')
plt.show()
