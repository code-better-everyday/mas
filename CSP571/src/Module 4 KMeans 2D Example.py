"""
Name: Module 4 KMeans 2D Example.py
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

# Set some options for printing all the columns
numpy.set_printoptions(precision = 10, threshold = sys.maxsize)
numpy.set_printoptions(linewidth = numpy.inf)

pandas.set_option('display.max_columns', None)
pandas.set_option('display.expand_frame_repr', False)
pandas.set_option('max_colwidth', None)

pandas.options.display.float_format = '{:,.10f}'.format

from sklearn import cluster, metrics

trainData = pandas.DataFrame({'x': [2.0, 4.0, 2.0, 4.0, 6.0, 8.0, 6.0, 8.0, 4.5, 5.5, 5.5, 4.5],
                              'y': [11.0, 11.0, 9.0, 9.0, 11.0, 11.0, 9.0, 9.0, 5.5, 5.5, 4.5, 4.5]})

feature_name = trainData.columns

# Specify the maximum number of clusters
max_nCluster = 11

nClusters = []
Elbow = []
Silhouette = []
TotalWCSS = []

# Try each number of cluster
for k in range(max_nCluster):

   # Train a k-means algorithm
   nCluster = k + 1
   objCluster = cluster.KMeans(n_clusters = nCluster, init = 'random',
                               n_init = 10, random_state = 5712023)
   member = objCluster.fit_predict(trainData)
   centroid = pandas.DataFrame(objCluster.cluster_centers_, columns = feature_name)

   # Calculate the Silhouette Index
   if (nCluster > 1):
       S = metrics.silhouette_score(trainData, member)
   else:
       S = numpy.NaN

   # Calculate the Within-Cluster Sum of Squares and Cluster sizes
   WCSS = numpy.zeros(nCluster)
   nSize = numpy.zeros(nCluster)

   for i in range(nCluster):
      subset = trainData[member == i]
      diff = subset - centroid.iloc[i]
      nSize[i] = diff.shape[0]
      WCSS[i] = numpy.square(diff).sum().sum()

   # Calculate the Elbow values
   E = numpy.sum(numpy.divide(WCSS, nSize))
   T = numpy.sum(WCSS)

   nClusters.append(nCluster)
   Elbow.append(E)
   Silhouette.append(S)
   TotalWCSS.append(T)

plt.figure(figsize = (8,6), dpi = 200)
plt.plot(nClusters, TotalWCSS, marker = 'o', color = 'royalblue')
plt.xlabel('Number of Clusters')
plt.ylabel('Total Within-Cluster Sum of Squares')
plt.xticks(range(1,max_nCluster+1))
plt.grid()
plt.show()

plt.figure(figsize = (8,6), dpi = 200)
plt.plot(nClusters, Elbow, marker = 'o', color = 'royalblue')
plt.xlabel('Number of Clusters')
plt.ylabel('Elbow Value')
plt.xticks(range(1,max_nCluster+1))
plt.grid()
plt.show()

plt.figure(figsize = (8,6), dpi = 200)
plt.plot(nClusters, Silhouette, marker = 'o', color = 'royalblue')
plt.xlabel('Number of Clusters')
plt.ylabel('Silhouette Index')
plt.xticks(range(1,max_nCluster+1))
plt.grid()
plt.show()

result_df = pandas.DataFrame({'N Cluster': nClusters, 'Total WCSS': TotalWCSS,
                              'Elbow': Elbow, 'Silhouette': Silhouette})
