#!/usr/bin/env python

import json
import pandas as pd
import plotly.express as px  
import sklearn

import utils.dota_data_utils as dota_data_utils
from utils.dota_data_utils import DotaData




args = json.load(open('dota_data_config.json'))
data = DotaData(**args['dota_data'])
data.heroes_data
data.hbym_data
data.match_data



rank = list(data.dota_ranks.keys())[2]
data = data.combine_teams(enemy=False)





# ##########################
# ### logistic regression
# data.combined = data.hbym_data
# data.combined.replace(-1, 0, inplace=True)
# data.combined = data.match_data.merge(data.combined, how='left', on='match_id')
data.drop(columns=['match_seq_num', 'start_time', 'avg_mmr', 'num_mmr', 
                   'lobby_type', 'game_mode', 'avg_rank_tier', 'num_rank_tier',
                   'cluster', 'radiant_team', 'dire_team',], inplace=True)
# ##########

rank_data = data.loc[data['dota rank'] == rank]
rank_data = rank_data.copy()
rank_data.drop(columns=['duration', 'dota rank', 'Tean name', 'radiant_win'], inplace=True)
rank_data.set_index('match_id', inplace=True) 
rank_data = rank_data.astype('category') ### check if is correct (?)
# print(rank_data.astype('category'))

######## Logistic regression ########
### feature selection
data_y = list(rank_data['Team win'])
data_x = rank_data.copy()
data_x.drop(columns='Team win', inplace=True)
data_x = data_x.to_numpy()
###
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
logreg = LogisticRegression()
rfe = RFE(logreg, n_features_to_select=30)
rfe = rfe.fit(data_x, data_y)
# print(rfe.support_)

### significance of heroes
data_x = rank_data.copy()
data_x.drop(columns='Team win', inplace=True)
features_selected = data_x.columns[rfe.support_]
print(list(features_selected))
data_x = rank_data[features_selected]
data_x = data_x.to_numpy()
###
# import statsmodels.api as sm ### check if activate all this 
# # logit_model=sm.Logit(data_y, data_x)
# logit_model=sm.GLM(data_y, data_x)
# # result=logit_model.fit(maxiter=160)
# result=logit_model.fit()
# features_significant = features_selected[result.pvalues < 0.05]
# print(list(features_significant)) ### check if activate all this 
features_significant = features_selected

# ### final model
data_x = rank_data.copy()
data_x.drop(columns='Team win', inplace=True)
features_selected = data_x.columns[rfe.support_]
data_x = rank_data[features_significant]
data_x = data_x.to_numpy()
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(data_x, data_y, test_size=0.3)
###
from sklearn.linear_model import LogisticRegression
print('fitting logistic regression')
logreg = LogisticRegression()
logreg.fit(X_train, y_train)
y_pred = logreg.predict(X_test)

from sklearn.metrics import confusion_matrix, mean_squared_error, classification_report ### check how to improve this and the random forest
confusion_matrix = confusion_matrix(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred)
print('Accuracy of logistic regression classifier on test set: {:.2f}'.format(logreg.score(X_test, y_test)))
print(classification_report(y_test, y_pred))
print(confusion_matrix)
print(rmse)

from sklearn.ensemble import RandomForestRegressor
print('fitting random forest')
randfor = RandomForestRegressor(n_estimators = 1000, criterion = "absolute_error",
                                max_depth = None, oob_score = False, max_features = 5,
                                n_jobs = -1, bootstrap=True)
randfor.fit(X_train, y_train)
y_pred = randfor.predict(X_test)

from sklearn.metrics import confusion_matrix, mean_squared_error, classification_report
confusion_matrix = confusion_matrix(y_test, y_pred.round().astype(int))
rmse = mean_squared_error(y_test, y_pred.round().astype(int))
print('coefficient of determination of random forest classifier on test set: {:.2f}'.format(randfor.score(X_test, y_test)))
print(classification_report(y_test, y_pred.round().astype(int)))
print(confusion_matrix)
print(rmse)

from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
logit_roc_auc = roc_auc_score(y_test, logreg.predict(X_test))
fpr, tpr, thresholds = roc_curve(y_test, logreg.predict_proba(X_test)[:,1])
plt.figure()
plt.plot(fpr, tpr, label='Logistic Regression (area = %0.2f)' % logit_roc_auc)
plt.plot([0, 1], [0, 1],'r--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic')
plt.legend(loc="lower right")
plt.savefig('Log_ROC')
plt.show()
