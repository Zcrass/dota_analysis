#!/usr/bin/env python

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, mean_squared_error, classification_report
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVR, SVC, LinearSVC


import statsmodels.api as sm ### check if activate all this 


class DotaPredictionModels():
    def __init__(self, data_x, data_y):
        # self.method = method
        # self.model = self.select_method()
        self.data_y = data_y
        self.data_x = data_x
        data_x = data_x
        self.selected_features = data_x.columns

    # def select_method(self):
    #     if self.method == 'logistic':
    #         model = LogisticRegression()
    #     elif self.method == 'forest':
    #         model =  RandomForestRegressor(n_estimators = 1000, criterion = "absolute_error",
    #                                        max_depth = None, oob_score = False, max_features = 5,
    #                                        n_jobs = -1, bootstrap=True)
    #     elif self.method == 'svm':
    #         model = LinearSVR()
    #     return model

    def rec_feat_elim(self, feat2keep):
        # print('Reducing number of features')
        rfe = RFE(LogisticRegression(), n_features_to_select=feat2keep)
        rfe = rfe.fit(self.data_x.to_numpy(), self.data_y)
        self.select_features = self.data_x.columns[rfe.support_]
        self.data_x = self.data_x[self.select_features]
        return self

    def hero_significanceself(self):
        # print('calculating features significance')
        logit_model=sm.GLM(self.data_y, self.data_x)
        result=logit_model.fit()
        self.select_features = self.data_x.columns[result.pvalues < 0.05]
        self.data_x = self.data_x[self.select_features]
        return self

    def split_dataset(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.data_x, self.data_y, test_size=0.3)
        return self
    
    def train_model(self, method):
        if method == 'logistic':
            print('fitting logistic regression')
            self.model = LogisticRegression()
            self.model.fit(self.X_train, self.y_train)
            self.y_pred = self.model.predict(self.X_test)

        elif method == 'forest':
            print('fitting random forest')
            self.model =  RandomForestClassifier(n_estimators = 1000, criterion = "gini",
                                                max_depth = None, oob_score = False, max_features = 5,
                                                n_jobs = -1, bootstrap=True)
            self.model.fit(self.X_train, self.y_train)
            self.y_pred = self.model.predict(self.X_test)

        elif method == 'svm':
            print('fitting Linear Support Vector Classificator')
            # self.model = LinearSVR()
            self.model = LinearSVC()
            # self.model = SVC()
            self.model.fit(self.X_train, self.y_train)
            self.y_pred = self.model.predict(self.X_test)

        return self

    def test_model(self):
        from sklearn.metrics import confusion_matrix
        self.confusion_matrix = confusion_matrix(self.y_test, self.y_pred.round().astype(int))
        self.rmse = mean_squared_error(self.y_test, self.y_pred.round().astype(int))
        self.score = self.model.score(self.X_test, self.y_test)
        self.classification_report = classification_report(self.y_test, self.y_pred.round().astype(int))
        return self