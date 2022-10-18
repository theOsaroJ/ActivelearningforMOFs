#!/usr/bin/env python
# coding: utf-8

#importing important libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import math

#importing the ML libraries
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, RationalQuadratic, WhiteKernel, Matern
from sklearn.gaussian_process.kernels import ConstantKernel as C

#Reading the dataset
df = pd.read_csv('Prior.csv',delimiter=',')
df2 = pd.read_csv('CompleteData.csv',delimiter=',')

#Unseen array
X_test_1= np.linspace(1e-5,1e-4,9)
X_test_2= np.linspace(1.1e-4,1e-3,9)
X_test_3= np.linspace(1.1e-3,1e-2,9)
X_test_4= np.linspace(1.1e-2,1e-1,9)
X_test_5= np.linspace(1.1e-1,1,9)
X_test_6= np.linspace(1.1,10,9)
X_test_7= np.linspace(11,100,10)
X_test=np.concatenate([X_test_1,X_test_2,X_test_3,X_test_4,X_test_5,X_test_6,X_test_7]).flatten().reshape(-1,1)

#Reading the data
x = df.iloc[:,0].values
y = df.iloc[:,1].values
#Taking the error data as well
e = df.iloc[:,2].values

#from complete-original dataset
x2 = df2.iloc[:,0].values
y2 = df2.iloc[:,1].values

#Replacing y if some y value in zero
for i in range(len(y)):
  if (y[i] == 0):
      y[i] = 0.0001

#For y2
for i in range(len(y2)):
  if (y2[i] == 0):
      y2[i] = 0.0001

#Transforming 1D arrays to 2D
x = np.atleast_2d(x).flatten().reshape(-1,1)
y = np.atleast_2d(y).flatten().reshape(-1,1)

x_true = x
y_actual = y

#converting P to bars
x = x/(1.0e5)

#Taking logbase 10 of the input vector
x = np.log10(x)
y = np.log10(y)

#Taking the log of X_test
X_test = np.log10(X_test)

#Extracting the mean and std. dev for X_test
x_m = np.mean(X_test)
x_std = np.std(X_test,ddof=1)

#Standardising x and y in log-space
x_s = (x - x_m)/x_std

#Standardising X_test in log-space
X_test = (X_test - x_m)/x_std

#kernel selection (this is the kernel used in this study after checking out several kernels)
kernel = RationalQuadratic(length_scale=50, alpha=0.5,length_scale_bounds=(1e-8,1e8),alpha_bounds=(1e-8,1e8))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=50, normalize_y=True)

#Fitting our normalized data to the GP model
gp.fit(x_s,y)

# Make the prediction on the test data
y_pred, sigma = gp.predict(X_test, return_std=True)
rel_error = np.zeros(len(sigma))

#finding the relative error
for i in range(len(sigma)):
    rel_error[i] = abs(sigma[i]/abs(y_pred[i]))

#define the limit for uncertainty
lim = 0.02
Max = np.amax(rel_error)
index = np.argmax(rel_error)

#transforming the index to original pressure point
X_test = (X_test*x_std) + x_m
X_test = 10**(X_test)
X_test = 1e5*(X_test)

#checking the whether the maximum uncertainty is less than out desired limit
if (Max >= lim):
  Data = str(X_test[index])
  Data = Data.replace("[","")
  Data = Data.replace("]","")
  print(Data)
  print("NOT_DONE ")
  print(rel_error[index])
else:
  Data = str(X_test[index])
  Data = Data.replace("[","")
  Data = Data.replace("]","")
  print(Data)
  print("DONE")
  print("Final Maximum Error=", rel_error[index])

y_pred = 10**y_pred
pred= y_pred
rel_error = 100*(rel_error)

#defining relative root mean square error
#defining relative true error
rel_t = np.zeros(len(X_test))
for i in range(len(rel_t)):
  rel_t[i] = ((y_pred[i] - y2[i])/y2[i])

#Finding relative root mean square error
rrmse = 0
for i in range(len(rel_error)):
  rrmse = rrmse + (((y_pred[i] - y2[i])**2)/y2[i]**2)
  X= (((y_pred[i] - y2[i])**2)/y2[i]**2)
  #print(X_test[i],p2[i],t2[i],y_pred[i],y2[i])
rrmse = 100*(np.sqrt(rrmse))/len(rel_error)

#converting the true rel error in percentage
rel_t = 100*(abs(rel_t))

#finding the mean of relative error
rel_m = np.mean(rel_error)

#printing mean of rel error and rrmse for each iteration in a separate mean.csv file
os.system("echo -n "+str(rel_m)+","+str(rrmse)+" >> mean.csv")

##printing rel error and true rel. error in a error file
for i in range(len(rel_error)):
    #rounding off the error to 3 digits after decimals
    rel_t[i] = round(rel_t[i],3)
    rel_error[i] = round(rel_error[i],3)
    #printing them in the .csv files for error
    os.system("echo -n "+str(rel_error[i])+" >> rel.csv")
    os.system("echo -n "+str(rel_t[i])+" >> rel_true.csv")
    if ( i != (len(rel_error) - 1)):
        os.system("echo -n "+","+" >> rel.csv")
        os.system("echo -n "+","+" >> rel_true.csv")

#Printing the final predicted data
a=pd.DataFrame(pred,columns=['Predicted'])
a.to_csv('pred.csv',index=False)

#Printing the X_test
b=pd.DataFrame(X_test, columns=['X Test'])
b.to_csv('X_test.csv', index=False)
