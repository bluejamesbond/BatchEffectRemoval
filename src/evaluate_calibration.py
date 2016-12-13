'''
Created on Dec 5, 2016

@author: urishaham
'''

import os.path
from Calibration_Util import DataHandler as dh 
from Calibration_Util import FileIO as io
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import CostFunctions as cf
from sklearn import decomposition
from keras import backend as K
import ScatterHist as sh
from statsmodels.distributions.empirical_distribution import ECDF
from numpy import genfromtxt
import sklearn.preprocessing as prep
from keras.models import load_model
from keras import initializations

# configuration hyper parameters
denoise = True # whether or not to train a denoising autoencoder to remover the zeros

init = lambda shape, name:initializations.normal(shape, scale=.1e-4, name=name)
def init (shape, name = None):
    return initializations.normal(shape, scale=.1e-4, name=name)
setattr(initializations, 'init', init)

######################
###### get data ######
######################
# we load two CyTOF samples 

data = 'person1_baseline'

if data =='person1_baseline':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_baseline.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_baseline.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_baseline_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_baseline_label.csv')
    autoencoder =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_DAE.h5'))  
    ResNet =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_ResNet.h5'), custom_objects={'init':init})  
    MLP =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_baseline_MLP.h5'), custom_objects={'init':init})  
if data =='person2_baseline':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_baseline.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_baseline.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_baseline_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_baseline_label.csv')
    autoencoder =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_DAE.h5'))  
    ResNet =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_ResNet.h5'))  
    MLP =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_baseline_MLP.h5'))  
if data =='person1_3month':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_3month.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_3month.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day1_3month_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person1Day2_3month_label.csv')
    autoencoder =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_3month_DAE.h5'))  
    ResNet =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_3month_ResNet.h5'))  
    MLP =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person1_3month_MLP.h5'))  
if data =='person2_3month':
    sourcePath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_3month.csv')
    targetPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_3month.csv')
    sourceLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day1_3month_label.csv')
    targetLabelPath = os.path.join(io.DeepLearningRoot(),'Data/Person2Day2_3month_label.csv')
    autoencoder =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_3month_DAE.h5'))  
    ResNet =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_3month_ResNet.h5'))  
    MLP =  load_model(os.path.join(io.DeepLearningRoot(),'savedModels/person2_3month_MLP.h5'))  
   
source = genfromtxt(sourcePath, delimiter=',', skip_header=0)
target = genfromtxt(targetPath, delimiter=',', skip_header=0)

# pre-process data: log transformation, a standard practice with CyTOF data
target = dh.preProcessCytofData(target)
source = dh.preProcessCytofData(source) 

if denoise:
    source = autoencoder.predict(source)
    target = autoencoder.predict(target)

# rescale source to have zero mean and unit variance
# apply same transformation to the target
preprocessor = prep.StandardScaler().fit(source)
source = preprocessor.transform(source) 
target = preprocessor.transform(target)    


##############################
###### evaluate results ######
##############################

calibratedSource_resNet = ResNet.predict(source)
calibratedSource_MLP = MLP.predict(source)

##################################### qualitative evaluation: PCA #####################################
pca = decomposition.PCA()
pca.fit(target)

# project data onto PCs
target_sample_pca = pca.transform(target)
projection_before = pca.transform(source)
projection_after_ResNet = pca.transform(calibratedSource_resNet)
projection_after_MLP = pca.transform(calibratedSource_MLP)

# choose PCs to plot
pc1 = 0
pc2 = 1
axis1 = 'PC'+str(pc1)
axis2 = 'PC'+str(pc2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_before[:,pc1], projection_before[:,pc2], axis1, axis2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_after_ResNet[:,pc1], projection_after_ResNet[:,pc2], axis1, axis2)
sh.scatterHist(target_sample_pca[:,pc1], target_sample_pca[:,pc2], projection_after_MLP[:,pc1], projection_after_MLP[:,pc2], axis1, axis2)

##################################### qualitative evaluation: per-marker empirical cdfs #####################################

for i in range(target.shape[1]):
    targetMarker = target[:,i]
    beforeMarker = source[:,i]
    afterMarker = projection_after_ResNet[:,i]
    m = np.min([np.min(targetMarker), np.min(beforeMarker), np.min(afterMarker)])
    M = np.max([np.max(targetMarker), np.max(beforeMarker), np.max(afterMarker)])
    x = np.linspace(m, M, num=100)
    target_ecdf = ECDF(targetMarker)
    before_ecdf = ECDF(beforeMarker)
    after_ecdf = ECDF(afterMarker)   
    tgt_ecdf = target_ecdf(x)
    bf_ecdf = before_ecdf(x)
    af_ecdf = after_ecdf(x)    
    fig = plt.figure()
    a1 = fig.add_subplot(111)
    a1.plot(tgt_ecdf, color = 'blue') 
    a1.plot(bf_ecdf, color = 'red') 
    a1.plot(af_ecdf, color = 'green') 
    a1.set_xticklabels([])
    plt.legend(['target', 'before calibration', 'after calibration'], loc=0)
    plt.show()
       
##################################### Correlation matrices ##############################################
corrB = np.corrcoef(source, rowvar=0)
corrA_resNet = np.corrcoef(projection_after_ResNet, rowvar=0)
corrA_MLP = np.corrcoef(projection_after_ResNet, rowvar=0)

corrT = np.corrcoef(target, rowvar=0)
FB = corrT - corrB
FA_resNet = corrT - corrA_resNet
FA_MLP= corrT - corrA_MLP

NB = np.linalg.norm(FB, 'fro')
NA_resNet = np.linalg.norm(FA_resNet, 'fro')
NA_MLP = np.linalg.norm(FA_MLP, 'fro')


print('norm before calibration: ', str(NB))
print('norm after calibration (resNet): ', str(NA_resNet)) 
print('norm after calibration (MLP): ', str(NA_MLP)) 

fa_resNet = FA_resNet.flatten()
fa_MLP = FA_MLP.flatten()
fb = FB.flatten()

f = np.zeros((fa_resNet.shape[0],3))
f[:,0] = fb
f[:,1] = fa_resNet
f[:,2] = fa_MLP

fig = plt.figure()
plt.hist(f, bins = 20, normed=True, histtype='bar')
plt.legend(['before calib.', 'ResNet calib.', 'MLP calib.'], loc=1)
plt.yticks([])
plt.show()
##################################### quantitative evaluation: MMD #####################################
# MMD with the scales used for training 
sourceInds = np.random.randint(low=0, high = source.shape[0], size = 1000)
targetInds = np.random.randint(low=0, high = target.shape[0], size = 1000)

mmd_before = K.eval(cf.MMD(source,target).cost(K.variable(value=source[sourceInds]), K.variable(value=target[targetInds])))
mmd_after_resNet = K.eval(cf.MMD(calibratedSource_resNet,target).cost(K.variable(value=calibratedSource_resNet[sourceInds]), K.variable(value=target[targetInds])))
mmd_after_MLP = K.eval(cf.MMD(calibratedSource_MLP,target).cost(K.variable(value=calibratedSource_MLP[sourceInds]), K.variable(value=target[targetInds])))

print('MMD before calibration: ' + str(mmd_before))
print('MMD after calibration (resNet): ' + str(mmd_after_resNet))
print('MMD after calibration (MLP): ' + str(mmd_after_MLP))


##################################### CD8 sub-population #####################################
sourceLabels = genfromtxt(sourceLabelPath, delimiter=',', skip_header=0)
targetLabels = genfromtxt(targetLabelPath, delimiter=',', skip_header=0)

source_subPop = source[sourceLabels==1]
resNetCalibSubPop = calibratedSource_resNet[sourceLabels==1]
mlpCalibSubPop = calibratedSource_MLP[sourceLabels==1]
target_subPop = target[targetLabels==1]

marker1 = 13 #17 'IFNg'
marker2 = 19

axis1 = 'CD28'
axis2 = 'GZB'

sh.scatterHist(target_subPop[:,marker1], target_subPop[:,marker2], source_subPop[:,marker1], source_subPop[:,marker2], axis1, axis2)
sh.scatterHist(target_subPop[:,marker1], target_subPop[:,marker2], resNetCalibSubPop[:,marker1], resNetCalibSubPop[:,marker2], axis1, axis2)
sh.scatterHist(target_subPop[:,marker1], target_subPop[:,marker2], mlpCalibSubPop[:,marker1], mlpCalibSubPop[:,marker2], axis1, axis2)